Set sh = CreateObject("WScript.Shell")
sh.Run "cmd.exe /c """ & Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\")) & "DEMARRER.cmd""", 0, False
