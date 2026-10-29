# normaliser-crlf.ps1 — remet tous les .bat du pack en CRLF.
#
# Pourquoi : cmd.exe calcule la position des labels en supposant des fins de
# ligne CRLF. Un .bat en LF pur peut donc faire sauter un « goto » quelques
# lignes trop loin, sans erreur visible. Prouve sur mettre-a-jour.bat le
# 2026-10-28 : en LF le bloc d'erreur Python s'affichait partiellement faux.
#
# Usage : powershell -NoProfile -ExecutionPolicy Bypass -File normaliser-crlf.ps1
#         (option -Racine "D:\chemin\du\pack" si le script est ailleurs)
#
# Chaque fichier modifie est sauvegarde dans backups\ avant reecriture.

param(
    [string]$Racine = (Split-Path -Parent $PSCommandPath)
)

$ErrorActionPreference = 'Stop'
$Racine = (Resolve-Path -LiteralPath $Racine).Path
$backups = Join-Path $Racine 'backups'
if (-not (Test-Path -LiteralPath $backups)) {
    New-Item -ItemType Directory -Path $backups | Out-Null
}

$horodatage = Get-Date -Format 'yyyyMMdd-HHmmss'
$fichiers = Get-ChildItem -LiteralPath $Racine -Filter *.bat -File -Recurse |
    Where-Object { $_.FullName -notmatch '\\node_modules\\' -and $_.FullName -notmatch '\\backups\\' }

$modifies = 0
$deja = 0

foreach ($f in $fichiers) {
    $octets = [System.IO.File]::ReadAllBytes($f.FullName)
    if ($octets.Length -eq 0) { continue }

    # LF isole = 0x0A non precede de 0x0D
    $lfSeul = 0
    for ($i = 0; $i -lt $octets.Length; $i++) {
        if ($octets[$i] -eq 0x0A -and ($i -eq 0 -or $octets[$i - 1] -ne 0x0D)) { $lfSeul++ }
    }
    if ($lfSeul -eq 0) { $deja++; continue }

    $nom = "${horodatage}__bat__$($f.Name)"
    $dest = Join-Path $backups $nom
    $n = 1
    while (Test-Path -LiteralPath $dest) {
        $dest = Join-Path $backups ("${horodatage}__bat__{0}.{1}" -f $f.Name, $n)
        $n++
    }
    Copy-Item -LiteralPath $f.FullName -Destination $dest
    $texte = [System.IO.File]::ReadAllText($f.FullName)
    $texte = $texte -replace "`r`n", "`n"
    $texte = $texte -replace "`n", "`r`n"
    [System.IO.File]::WriteAllText($f.FullName, $texte, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host ("converti  : {0}  ({1} LF isoles)" -f $f.FullName, $lfSeul)
    $modifies++
}

Write-Host ("{0} fichier(s) converti(s), {1} deja en CRLF." -f $modifies, $deja)
