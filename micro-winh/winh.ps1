param([string]$Touche = 'h')

# Journal minimal, sans interpolation fragile : c'est la toute premiere chose ecrite.
$log = 'J:\Reasonix\dev\voix-winh\winh.log'
try {
    Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + ' DEPART')
} catch {}

try {
    $code = @"
using System;
using System.Runtime.InteropServices;
[StructLayout(LayoutKind.Sequential)]
public struct KEYBDINPUT { public ushort wVk; public ushort wScan; public uint dwFlags; public uint time; public IntPtr dwExtraInfo; }
[StructLayout(LayoutKind.Sequential)]
public struct MOUSEINPUT { public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo; }
[StructLayout(LayoutKind.Sequential)]
public struct HARDWAREINPUT { public uint uMsg; public ushort wParamL; public ushort wParamH; }
[StructLayout(LayoutKind.Explicit)]
public struct INPUTUNION { [FieldOffset(0)] public MOUSEINPUT mi; [FieldOffset(0)] public KEYBDINPUT ki; [FieldOffset(0)] public HARDWAREINPUT hi; }
[StructLayout(LayoutKind.Sequential)]
public struct INPUT { public uint type; public INPUTUNION u; }
public class Touche {
    [DllImport("user32.dll", SetLastError = true)] public static extern uint SendInput(uint n, INPUT[] p, int cb);
    [DllImport("user32.dll")] public static extern uint MapVirtualKey(uint code, uint type);
    public static uint Un(ushort vk, ushort scan, uint flags) {
        INPUT[] s = new INPUT[1];
        s[0].type = 1; s[0].u.ki.wVk = vk; s[0].u.ki.wScan = scan; s[0].u.ki.dwFlags = flags;
        return SendInput(1, s, Marshal.SizeOf(typeof(INPUT)));
    }
}
"@
    Add-Type -TypeDefinition $code
    Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + ' Add-Type OK')

    $EXT = 1; $UP = 2; $SC = 8
    $vkT = [uint32][char]$Touche.ToUpper()
    $scT = [Touche]::MapVirtualKey($vkT, 0)
    Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + " scan=$scT")

    $r1 = [Touche]::Un(0, 0x5B, ($SC -bor $EXT))
    Start-Sleep -Milliseconds 60
    $r2 = [Touche]::Un(0, $scT, $SC)
    Start-Sleep -Milliseconds 40
    $r3 = [Touche]::Un(0, $scT, ($SC -bor $UP))
    Start-Sleep -Milliseconds 40
    $r4 = [Touche]::Un(0, 0x5B, ($SC -bor $EXT -bor $UP))
    Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + " envois=$r1$r2$r3$r4")

    # Garder le processus vivant pendant la dictee : s'il meurt trop tot,
    # Windows peut reprendre le focus et couper la session.
    Start-Sleep -Seconds 15
    Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + ' fin de veille')
} catch {
    try {
        Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + ' ERREUR : ' + $_.Exception.Message)
    } catch {}
    exit 1
}
