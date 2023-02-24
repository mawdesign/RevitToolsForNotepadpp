# -*- coding: utf-8 -*-
from pyrevit import revit
from pyrevit import script
import os
import subprocess

def Open (file = "", path = "", syntax = "", exepath = None):
    # get Notepad path
    if exepath == None:
        cfg = script.get_config("Notepad++")
        exepath = cfg.get_option('notepadpath', os.path.join(os.environ["ProgramFiles"],"Notepad++", "Notepad++.exe"))

    # get file path
    if file == "keynote":
        # get keynote file path
        path = revit.query.get_local_keynote_file(doc=revit.doc)
        syntax = "-lprops"
    elif file == "shared parameters":
        # get shared parameters file path
        app = __revit__.Application
        path = app.SharedParametersFilename
        syntax = "-lprops"
    elif file == "keyboard shortcuts":
        # get keyboard shortcuts file path
        path = os.path.expandvars("%APPDATA%\Autodesk\Revit\Autodesk Revit 2021\KeyboardShortcuts.xml")
        syntax = "-lxml"
    elif file == "current journal":
        # get journal file file path
        path = revit.get_current_journal_file()
        syntax = "-lvb -n9999999999"
# - Revit ini (user/install)
# - C:\Users\mwarwick\AppData\Roaming\Autodesk\Revit\Autodesk Revit 2021\RevitUILayout.xml
# - environment file
    else:
        path = ""
        syntax = ""
    
    # open Notepad(++) with file
    path = os.path.realpath(path)
    if not exepath is None and os.path.exists(exepath):
        command = u'start "Notepad++" {0} {2} "{1}"'.format(exepath, path, syntax)
        os.system(command)
