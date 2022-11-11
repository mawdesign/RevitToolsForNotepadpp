# from pyrevit import forms
from pyrevit import revit
from pyrevit import script
import os
import subprocess

# get shared parameter path
app = __revit__.Application
spfile = app.SharedParametersFilename
# forms.alert(spfile,warn_icon=False)

# get path to notepad++
cfg = script.get_config("Notepad++")
exepath = cfg.get_option('notepadpath', os.path.join(os.environ["ProgramFiles"],"Notepad++", "Notepad++.exe"))
if not exepath is None and os.path.exists(exepath):
    subprocess.Popen([exepath,spfile,"-lprops"])
