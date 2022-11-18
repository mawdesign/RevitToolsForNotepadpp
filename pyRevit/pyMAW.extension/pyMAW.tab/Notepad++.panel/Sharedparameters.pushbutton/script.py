from pyrevit import revit, DB
from pyrevit import script
import os
import subprocess
import re
import random

doc = revit.doc
elements = []
groupnames = []
groups = {}
groupno = int(random.random()*6) * 10 + 30
text = ""

# get shared parameters from project
sp_collector = (
    DB.FilteredElementCollector(doc)
    .WhereElementIsNotElementType()
    .OfClass(DB.SharedParameterElement)
)

for sp in sp_collector:
    sp_def = sp.GetDefinition()
    elements.append({"Name" : sp.Name,
    "Id" : sp.Id,
    "GUID" : sp.GuidValue,
    "Group" : str(sp_def.ParameterGroup).replace("PG_","").replace("INVALID","OTHER").replace("AELECTRICAL","ELECTRICAL").replace("ADSK_","").replace("_"," ").title(),
    "Type" : sp_def.ParameterType,
    "Visible" : sp_def.Visible,
    "HideWhenNoValue" : sp.ShouldHideWhenNoValue(),
    })

# get path to executable
cfg = script.get_config("Notepad++")
exepath = cfg.get_option('notepadpath', os.path.join(os.environ["ProgramFiles"],"Notepad++", "Notepad++.exe"))
if not exepath is None and os.path.exists(exepath):
    docname = __revit__.ActiveUIDocument.Document.Title
    docname = re.sub('.rfa$', '', docname)
    docname += "_SharedParams"
    filepath = script.get_instance_data_file(docname)
    if filepath:
        # export list of shared parameters as [id] name
        # allows select by ID and manual delete in Revit
        for sp in sorted(elements, key=lambda sp: sp["Name"].lower()):
            text += "[{}]\t{}\r\n".format(sp["Id"], sp["Name"])
            if not sp["Group"] in groupnames:
                groupnames.append(sp["Group"])
        for g in sorted(groupnames):
            groups[g] = groupno
            groupno += 1
        # export shared parameters as shared parameter file
        # groups named by "Group parameter under" value
        # group numbers are random values > 40 to allow copy/paste into existing SP files with minimum overlap
        text += """\r\n\r\n# This is a Revit shared parameter file.
# Do not edit manually.
*META	VERSION	MINVERSION
META	2	1
*GROUP	ID	NAME\r\n"""
        for g in sorted(groupnames):
            text += "GROUP\t{}\t{}\r\n".format(groups[g], g)
        text += "*PARAM	GUID	NAME	DATATYPE	DATACATEGORY	GROUP	VISIBLE	DESCRIPTION	USERMODIFIABLE	HIDEWHENNOVALUE\r\n" 
        for sp in sorted(sorted(elements, key=lambda sp: sp["Name"].lower()), key=lambda e: e["Group"]):
            text += "PARAM\t{}\t{}\t{}\t\t{}\t{}\t\t1\t{}\r\n".format(sp["GUID"], sp["Name"], str(sp["Type"]).upper(), groups[sp["Group"]],
            1 if sp["Visible"] else 0, 1 if sp["HideWhenNoValue"] else 0)
        text += "\r\n" 
        file = revit.files.write_text(filepath, text)
        subprocess.Popen([exepath,filepath,"-llisp"])
