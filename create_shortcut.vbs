
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "C:\Users\Luciano\Desktop\Migrador Delphi.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "C:\Users\Luciano\AppData\Local\Programs\Python\Python311\pythonw.exe"
oLink.Arguments = "C:\Users\Luciano\Desktop\delphi-migration\migrador_delphi.py"
oLink.WorkingDirectory = "C:\Users\Luciano\Desktop\delphi-migration"
oLink.IconLocation = "C:\Users\Luciano\AppData\Local\Programs\Python\Python311\python.exe"
oLink.Save
