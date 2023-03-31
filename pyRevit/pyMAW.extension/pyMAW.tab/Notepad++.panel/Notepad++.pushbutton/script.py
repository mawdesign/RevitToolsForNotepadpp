from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
import os
import subprocess

cfg = script.get_config("Notepad++")
exepath = cfg.get_option(
    "notepadpath",
    os.path.join(os.environ["ProgramFiles"], "Notepad++", "Notepad++.exe"),
)
if not exepath is None and os.path.exists(exepath):
    subprocess.Popen([], executable=exepath)
else:
    if exepath is None:
        msg = "Path to Notepad++ not configured. Use <shift-click> to edit the configuration"
    else:
        msg = (
            "The file "
            + exepath
            + " could not be found. Use <shift-click> to edit the configuration"
        )
    forms.alert("Notepad++ not found", sub_msg=msg, ok=True)
