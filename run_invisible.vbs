On Error Resume Next

' Get the directory where this VBS script is located
Dim fso, scriptPath, scriptDir
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = WScript.ScriptFullName
scriptDir = fso.GetParentFolderName(scriptPath)

' Create shell object
Set WshShell = CreateObject("WScript.Shell")

' Run the batch file in VISIBLE mode (window mode 1)
' When SHOW_MESSAGE = False, window will flash briefly and close
' When SHOW_MESSAGE = True, popup will stay visible
WshShell.Run "cmd /c cd /d """ & scriptDir & """ && run_task.bat", 1, False

' Clean up
Set WshShell = Nothing
Set fso = Nothing

