# минимально — работает на Windows
import subprocess

cmd = r'powershell -NoProfile -Command "Add-Type -MemberDefinition @\'using System; using System.Text; using System.Runtime.InteropServices; public static class W{ [DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow(); [DllImport(\"user32.dll\", CharSet=CharSet.Auto)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount); [DllImport(\"user32.dll\")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);} \'@ -Name WinApi -Namespace WinLib; $h=[WinLib.WinApi]::GetForegroundWindow(); $sb=New-Object System.Text.StringBuilder 1024; [WinLib.WinApi]::GetWindowText($h,$sb,$sb.Capacity) > $null; [WinLib.WinApi]::GetWindowThreadProcessId($h,[ref]$pid) > $null; Write-Output \"Title: $($sb.ToString())\"; Write-Output \"PID: $pid;\"; try{ Write-Output \"Process: \" + (Get-Process -Id $pid).ProcessName } catch { Write-Output \"Process: (unknown or access denied)\" }"'

# Скрыть окно, захватить вывод
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
si.wShowWindow = subprocess.SW_HIDE

proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=si)
print(proc.stdout)
print(proc.stderr)
