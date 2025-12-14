' Discord Dev Bot - Silent Startup Script

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get script directory
ScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Python path (full path)
PythonPath = "C:\Python313\pythonw.exe"

' If pythonw.exe not found, try python.exe
If Not fso.FileExists(PythonPath) Then
    PythonPath = "C:\Python313\python.exe"
End If

' Bot script path
BotPath = ScriptDir & "\bot.py"

' Run in background (window hidden)
WshShell.Run """" & PythonPath & """ """ & BotPath & """", 0, False