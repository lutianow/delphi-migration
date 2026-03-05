import sys
import os
import shutil

# Pega o caminho real do Python (o mesmo que roda a interface)
python_exe = sys.executable

# A partir do python.exe tentamos adivinhar o pythonw.exe (que roda sem terminal preto)
pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")

if not os.path.exists(pythonw_exe):
    # Se não existir, foca no python.exe mesmo.
    pythonw_exe = python_exe

script_vbs = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Migrador Delphi.lnk')}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{pythonw_exe}"
oLink.Arguments = "{os.path.abspath('migrador_delphi.py')}"
oLink.WorkingDirectory = "{os.path.abspath('.')}"
oLink.IconLocation = "{python_exe}"
oLink.Save
"""

with open("create_shortcut.vbs", "w") as f:
    f.write(script_vbs)

print(os.system("cscript //nologo create_shortcut.vbs"))
