from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
import os
import subprocess

family_properties = []
text = ""

def get_parameters():
    # get list of parameters to be exported from user
    fm = revit.doc.FamilyManager
    return forms.SelectFromList.show(
        [x.Definition.Name for x in fm.GetParameters()],
        title="Select Parameters",
        multiselect=True,
    ) or []

def get_parameter_properties(params):
    #get parameters of a parameter
    fm = revit.doc.FamilyManager
    return [{"Name" : x.Definition.Name, "Formula" : x.Formula or ""} for x in fm.GetParameters()
                      if x.Definition.Name in params]

if __name__ == '__main__':
    forms.check_familydoc(exitscript=True)
    filepath = script.get_document_data_file("formulas", "tmp")
    if filepath:
        family_params = get_parameters()
        family_properties = get_parameter_properties(family_params)
        for fp in family_properties:
            text += "[{Name}]\r\n{Formula}\r\n\r\n".format(**fp) 
        # output = script.get_output()
        # output.print_code(text)
        file = revit.files.write_text(filepath, text)
        subprocess.Popen(['C:\\Users\\Warwickm\\OneDrive - Warren and Mahoney\\Documents\\PortableApps\\Notepad++Portable\\Notepad++Portable.exe',filepath,"-llisp"])



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
