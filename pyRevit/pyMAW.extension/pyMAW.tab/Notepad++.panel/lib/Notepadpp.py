# -*- coding: utf-8 -*-
from pyrevit import revit
from pyrevit import script
from pyrevit import HOST_APP
import os
import subprocess

def Open (file = "", path = "", syntax = "", exepath = None):
    revit_ver = HOST_APP.version
    logger = script.get_logger()
    
    # get Notepad path
    if exepath == None:
        cfg = script.get_config("Notepad++")
        exepath = cfg.get_option('notepadpath', os.path.join(os.environ["ProgramFiles"], "Notepad++", "Notepad++.exe"))

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
    elif file == "user revit.ini":
        # get user revit.ini file path
        path = os.path.expandvars("%APPDATA%\Autodesk\Revit\Autodesk Revit {0}\Revit.ini".format(revit_ver))
        syntax = "-lini"
    elif file == "default revit.ini":
        # get default revit.ini file path
        path = os.path.expandvars("%ALLUSERSPROFILE%\Autodesk\RVT {0}\UserDataCache\Revit.ini".format(revit_ver))
        syntax = "-lini"
    elif file == "keyboard shortcuts":
        # get keyboard shortcuts file path
        path = os.path.expandvars("%APPDATA%\Autodesk\Revit\Autodesk Revit {0}\KeyboardShortcuts.xml".format(revit_ver))
        syntax = "-lxml"
    elif file == "revit server settings":
        # get revit server settings file path
        path = os.path.expandvars("%PROGRAMDATA%\Autodesk\Revit Server {0}\Config\RSN.ini".format(revit_ver))
        syntax = "-lini"
    elif file == "ifc export categories":
        # get IFC export category table file path
        app = __revit__.Application
        path = app.ExportIFCCategoryTable
        syntax = "-lpowershell"
    elif file == "current journal":
        # get journal file file path
        path = revit.get_current_journal_file()
        syntax = "-lvb -n9999999999"
    # other ideas:
    # - C:\Users\mwarwick\AppData\Roaming\Autodesk\Revit\Autodesk Revit 2021\RevitUILayout.xml
    # - environment file
    else:
        path = ""
        syntax = ""
    
    # open Notepad(++) with file
    if not exepath is None and os.path.exists(exepath):
        if len(path) > 0:
            path = '"' + os.path.realpath(path) + '"'
        command = u'start "Notepad++" "{0}" {1} {2}'.format(exepath, syntax, path)
        logger.debug(command)
        os.system(command)
