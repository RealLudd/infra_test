' Debug version - shows errors in a message box
On Error Resume Next

' Get the directory where this VBS script is located
Dim fso, scriptPath, scriptDir
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = WScript.ScriptFullName
scriptDir = fso.GetParentFolderName(scriptPath)

' Create shell object
Set WshShell = CreateObject("WScript.Shell")

' Change to script directory and run the batch file invisibly
WshShell.CurrentDirectory = scriptDir
WshShell.Run """" & scriptDir & "\run_task.bat""", 0, False

' Check for errors
If Err.Number <> 0 Then
    MsgBox "Error running task:" & vbCrLf & _
           "Number: " & Err.Number & vbCrLf & _
           "Description: " & Err.Description & vbCrLf & _
           "Script Dir: " & scriptDir, vbCritical, "BPA Task Error"
    Err.Clear
End If

' Clean up
Set WshShell = Nothing
Set fso = Nothing

