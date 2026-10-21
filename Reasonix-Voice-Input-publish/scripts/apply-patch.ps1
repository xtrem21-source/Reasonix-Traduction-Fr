<#
  apply-patch.ps1 - Reasonix Voice Input
  ---------------------------------------------------------------------------
  Installs or updates the voice input button in the installed Reasonix Studio.

  Reasonix Studio is an Electron shell whose UI is a PLAIN folder:
      <AppDir>\resources\frontend-next\dist
  There is no app.asar repack: this script copies voice-input.js into that
  folder and injects one <script> tag into index.html.

  The app is NOT closed by this script. The frontend is served from disk; after
  patching, reload the page (Ctrl+R) or relaunch Reasonix Studio.

  Usage:
      .\apply-patch.ps1
      .\apply-patch.ps1 -Force                 (re-apply / repair)
      .\apply-patch.ps1 -Rollback              (restore index.html.bak)
      .\apply-patch.ps1 -Check                 (read-only state check)
      .\apply-patch.ps1 -FrontendDir "C:\...\dist" -ScriptPath "..\src\voice-input.reasonix.js"

  This file is intentionally ASCII: Windows PowerShell 5.1 reads a script
  without BOM as ANSI, and non-ASCII characters can break parsing.
#>

[CmdletBinding()]
param(
    [string]$AppDir = (Join-Path $env:LOCALAPPDATA 'Programs\Reasonix Studio'),
    [string]$FrontendDir,
    [string]$HtmlRel = 'index.html',
    [string]$JsRel = 'voice-input.js',
    [string]$ScriptPath,
    [string]$LogFile,

    [switch]$Rollback,
    [switch]$Force,
    [switch]$Check,
    [switch]$BackupOnly
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
$script:LogFile = $LogFile

function Write-Log {
    param(
        [string]$Message,
        [string]$Color = 'Gray'
    )
    $line = ('[{0}] {1}' -f (Get-Date -Format 'HH:mm:ss'), $Message)
    Write-Host $line -ForegroundColor $Color
    if ($script:LogFile) {
        try { Add-Content -Path $script:LogFile -Value $line -Encoding UTF8 } catch { }
    }
}

if (-not $FrontendDir) {
    $FrontendDir = Join-Path $AppDir 'resources\frontend-next\dist'
}

$html    = Join-Path $FrontendDir $HtmlRel
$jsDest  = Join-Path $FrontendDir $JsRel
$bak     = $html + '.bak'
$shaFile = $bak + '.sha256'
$root    = Split-Path $PSScriptRoot -Parent
$oldDir  = Join-Path $root 'old'
$logsDir = Join-Path $root 'logs'

if (-not $ScriptPath) {
    $ScriptPath = Join-Path $root 'src\voice-input.reasonix.js'
}

if (-not $script:LogFile) {
    if (-not (Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }
    $script:LogFile = Join-Path $logsDir ('patch-ReasonixStudio-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
}

Write-Log '' 'White'
Write-Log '=== Reasonix Voice Input ===' 'Cyan'
Write-Log ('Date      : ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) 'DarkGray'
Write-Log ('frontend  : ' + $FrontendDir) 'DarkGray'
Write-Log ('html      : ' + $html) 'DarkGray'
Write-Log ('script    : ' + $ScriptPath) 'DarkGray'

function Get-Sha256 {
    param([string]$Path)
    return (Get-FileHash -Path $Path -Algorithm SHA256).Hash
}

function Write-ShaFile {
    param([string]$HashValue)
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($shaFile, $HashValue + "`r`n", $enc)
}

function Test-BackupChecksum {
    param([string]$BakHash)
    if (-not (Test-Path $shaFile)) {
        return $false
    }
    $expected = ([System.IO.File]::ReadAllText($shaFile)).Trim()
    return ($expected -eq $BakHash)
}

try {
    if (-not (Test-Path $html)) {
        throw ('index.html not found: ' + $html + '. Check the Reasonix Studio install path.')
    }

    $running = @(Get-Process -Name 'Reasonix Studio' -ErrorAction SilentlyContinue)
    if ($running.Count -gt 0) {
        if ($BackupOnly -or $Check -or $Rollback) {
            Write-Log 'Reasonix Studio is running. This operation does not need to close it.' 'DarkGray'
        }
        else {
            Write-Log 'Reasonix Studio is running. The patch is written to disk; reload (Ctrl+R) or relaunch to activate it.' 'Yellow'
        }
    }

    # --- check (no writes) ---------------------------------------------------
    if ($Check) {
        $text = [System.IO.File]::ReadAllText($html)
        $tagged = $text.Contains('voice-input.js')
        $jsExists = Test-Path $jsDest
        $sameHash = $false
        if ($jsExists -and (Test-Path $ScriptPath)) {
            $sameHash = ((Get-Sha256 $jsDest) -eq (Get-Sha256 $ScriptPath))
        }
        $bakExists = Test-Path $bak
        $bakHash = if ($bakExists) { Get-Sha256 $bak } else { '' }
        $bakShaOk = if ($bakExists) { Test-BackupChecksum $bakHash } else { $false }
        Write-Log ('check: html tagged = ' + $tagged + ', voice-input.js present = ' + $jsExists + ', hash matches source = ' + $sameHash + ', backup present = ' + $bakExists + ', backup sha256 = ' + $bakShaOk) $(if ($tagged -and $jsExists -and $sameHash -and $bakExists -and $bakShaOk) { 'Green' } else { 'Yellow' })
        $exitCode = if ($tagged -and $jsExists -and $sameHash -and $bakExists -and $bakShaOk) { 0 } else { 1 }
        exit $exitCode
    }

    # --- backup only (no patch) ---------------------------------------------
    if ($BackupOnly) {
        $text = [System.IO.File]::ReadAllText($html)
        if ($text.Contains('voice-input.js')) {
            if (-not (Test-Path $bak)) {
                throw ('Already patched and no clean backup at ' + $bak + '. Cannot prepare a clean backup.')
            }
            Write-Log ('Already patched; existing backup kept: ' + $bak) 'Yellow'
            exit 0
        }
        $origHash = Get-Sha256 $html
        Copy-Item $html $bak -Force
        $bakHash = Get-Sha256 $bak
        if ($origHash -ne $bakHash) {
            throw 'Backup verification failed: the copy does not match index.html. Aborting.'
        }
        Write-ShaFile $origHash
        if (-not (Test-Path $oldDir)) {
            New-Item -ItemType Directory -Path $oldDir -Force | Out-Null
        }
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $archive = Join-Path $oldDir ('index.html.' + $stamp)
        Copy-Item $html $archive -Force
        Write-Log ('OK - backup ready (verified).') 'Green'
        Write-Log ('Backup    : ' + $bak) 'DarkGray'
        Write-Log ('Checksum  : ' + $shaFile) 'DarkGray'
        Write-Log ('Archive   : ' + $archive) 'DarkGray'
        Write-Log 'No patch was applied. You can now run the installer.' 'DarkGray'
        exit 0
    }

    # --- rollback ------------------------------------------------------------
    if ($Rollback) {
        if (-not (Test-Path $bak)) {
            throw ('No backup found: ' + $bak + '. Nothing was restored.')
        }
        $bakHash = Get-Sha256 $bak
        if ((Test-Path $shaFile) -and -not (Test-BackupChecksum $bakHash)) {
            throw ('Backup checksum mismatch: ' + $bak + '. The backup may be corrupted. Use old/ or docs/reference/.')
        }
        Copy-Item $bak $html -Force
        if (Test-Path $jsDest) {
            Remove-Item $jsDest -Force
        }
        $restoredHash = Get-Sha256 $html
        if ($restoredHash -ne $bakHash) {
            throw 'Rollback verification failed: index.html does not match the backup.'
        }
        Write-Log ('OK - index.html restored from backup (' + $restoredHash.Substring(0, 16) + '...) and voice-input.js removed.') 'Green'
        Write-Log 'Reload or relaunch Reasonix Studio.' 'DarkGray'
        exit 0
    }

    if (-not (Test-Path $ScriptPath)) {
        throw ('Source script not found: ' + $ScriptPath)
    }

    $text = [System.IO.File]::ReadAllText($html)
    $isPatched = $text.Contains('voice-input.js')

    if ($isPatched -and -not $Force) {
        throw 'This index.html is already patched. Use -Force to re-apply, or -Rollback to remove.'
    }

    if ($isPatched) {
        if (-not (Test-Path $bak)) {
            throw ('Already patched and no clean backup at ' + $bak + '. Reinstall Reasonix Studio, then run without -Force.')
        }
        $bakHash = Get-Sha256 $bak
        if ((Test-Path $shaFile) -and -not (Test-BackupChecksum $bakHash)) {
            throw ('Backup checksum mismatch: ' + $bak + '. Reinstall Reasonix Studio or use old/.')
        }
        $bakText = [System.IO.File]::ReadAllText($bak)
        if ($bakText.Contains('voice-input.js')) {
            throw 'The backup itself is patched; it cannot be used as a clean restore point.'
        }
        Write-Log 'Already patched -> restoring the clean backup before re-applying.' 'Yellow'
        Copy-Item $bak $html -Force
    }
    else {
        # Current file is clean: create and VERIFY the backup before any write.
        $origHash = Get-Sha256 $html
        Copy-Item $html $bak -Force
        $bakHash = Get-Sha256 $bak
        if ($origHash -ne $bakHash) {
            throw 'Backup verification failed: the copy does not match index.html. Aborting before any modification.'
        }
        Write-ShaFile $origHash
        if (-not (Test-Path $oldDir)) {
            New-Item -ItemType Directory -Path $oldDir -Force | Out-Null
        }
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $archive = Join-Path $oldDir ('index.html.' + $stamp)
        Copy-Item $html $archive -Force
        Write-Log ('Backup    : ' + $bak + ' (verifie)') 'Green'
        Write-Log ('Checksum  : ' + $shaFile) 'DarkGray'
        Write-Log ('Archive   : ' + $archive) 'DarkGray'
    }

    # --- copy the script -----------------------------------------------------
    Copy-Item $ScriptPath $jsDest -Force
    Write-Log ('Added     : ' + $JsRel) 'Green'

    # --- inject the script tag ----------------------------------------------
    $text = [System.IO.File]::ReadAllText($html)
    if ($text -notmatch 'voice-input\.js') {
        $tag = '<script src="./voice-input.js"></script>'
        $repl = '  ' + $tag + "`r`n</body>"
        $text = [regex]::Replace($text, '</body>', $repl, 'IgnoreCase')
        $enc = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($html, $text, $enc)
        Write-Log ('Injected  : <script> into ' + $HtmlRel) 'Green'
    }
    else {
        Write-Log ('Injected  : tag already present in ' + $HtmlRel + ' (skipped)') 'Yellow'
    }

    # --- verify --------------------------------------------------------------
    $text = [System.IO.File]::ReadAllText($html)
    if (-not $text.Contains('voice-input.js')) {
        throw 'Verification failed: the script tag is missing after injection.'
    }
    if (-not (Test-Path $jsDest)) {
        throw 'Verification failed: voice-input.js was not copied.'
    }
    $srcHash = Get-Sha256 $ScriptPath
    $dstHash = Get-Sha256 $jsDest
    if ($srcHash -ne $dstHash) {
        throw ('Verification failed: hash mismatch (' + $dstHash + ' != ' + $srcHash + ').')
    }

    Write-Log ('OK - patched. voice-input.js = ' + $dstHash.Substring(0, 16) + '...') 'Green'
    Write-Log 'Reload the page (Ctrl+R) or relaunch Reasonix Studio.' 'Green'
    Write-Log 'RETOUR ARRIERE: double-click RESTAURER-MIC-REASONIX.bat (or .\scripts\apply-patch.ps1 -Rollback).' 'Yellow'
    Write-Log 'La sauvegarde a ete verifiee avant toute modification; son empreinte est dans index.html.bak.sha256.' 'DarkGray'
}
catch {
    Write-Log ('ECHEC : ' + $_.Exception.Message) 'Red'
    if ($_.Exception.StackTrace) { Write-Log ('  ' + $_.Exception.StackTrace) 'DarkGray' }
    exit 1
}

Write-Log ('Journal   : ' + $script:LogFile) 'DarkGray'
exit 0
