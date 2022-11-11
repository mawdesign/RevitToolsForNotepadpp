from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
import os
import subprocess

family_properties = []
text = ""

def try_or(fn, default = None):
    try:
        return fn()
    except:
        return default

def get_parameters():
    # get list of parameters to be exported
    fm = revit.doc.FamilyManager
    return [{"Name" : x.Definition.Name, 
        "Formula" : x.Formula or "",
        "Type" : x.Definition.ParameterType,
        "isShared" : x.IsShared,
        "GUID" : try_or(lambda: x.GUID, "")
        } for x in fm.GetParameters()]

# get path to executable
cfg = script.get_config("Notepad++")
exepath = cfg.get_option('notepadpath', os.path.join(os.environ["ProgramFiles"],"Notepad++", "Notepad++.exe"))
if not exepath is None and os.path.exists(exepath):
    forms.check_familydoc(exitscript=True)
    filepath = script.get_document_data_file("formulas", "tmp")
    if filepath:
        for fp in get_parameters():
            text += "[{}] {}\r\n".format(fp["Name"], str(fp["Type"]).upper())
            text += "{}\r\n".format(fp["Formula"]) if fp["Formula"] != "" else ""
            text += "\r\n" 
        file = revit.files.write_text(filepath, text)
        subprocess.Popen([exepath,filepath,"-llisp"])


# pname.append(param.Definition.Name)
# try:guid.append(param.GUID)
# except: guid.append(None)
# pgroup.append(param.Definition.ParameterGroup)
# ptype.append(param.Definition.ParameterType)
# utype.append(param.Definition.UnitType)
# try: dutype.append(param.DisplayUnitType)
# except: dutype.append(None)
# stype.append(param.StorageType)
# isinstance.append(param.IsInstance)
# isreporting.append(param.IsReporting)
# isshared.append(param.IsShared)
# isreadonly.append(param.IsReadOnly)
# usermodifiable.append(param.UserModifiable)
# formula.append(param.Formula)
# determinedbyformula.append(param.IsDeterminedByFormula)
# assocparams = param.AssociatedParameters
# associatedparams.append(assocparams)
# assocelems = list()
# for assoc in assocparams:
    # assocelems.append(assoc.Element)
# associatedelements.append(assocelems)
# canassignformula.append(param.CanAssignFormula)
