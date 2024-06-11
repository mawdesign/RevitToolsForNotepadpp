# -*- coding: utf-8 -*-

from pyrevit import revit
from pyrevit import script
from pyrevit import HOST_APP
import os, codecs

# import subprocess

dynamoVerList = {
    "2020.0": "2.3",
    "2020.1": "2.3",
    "2020.2": "2.3",
    "2021.0": "2.5",
    "2021.1": "2.6",
    "2022.0": "2.10",
    "2022.1": "2.12",
    "2023": "2.13",
    "2023.1": "2.16",
    "2024": "2.17",
    "2024.1": "2.18",
}


def OpenNpp(path="", options="", exepath=None):
    logger = script.get_logger()

    # get Notepad path
    if exepath == None:
        cfg = script.get_config("Notepad++")
        exepath = cfg.get_option(
            "notepadpath",
            os.path.join(os.environ["ProgramFiles"], "Notepad++", "Notepad++.exe"),
        )

    # open Notepad(++) with file
    if len(path) > 0:
        path = '"' + os.path.realpath(path) + '"'
    if not exepath is None and os.path.exists(exepath):
        command = 'start "Notepad++" "{0}" {1} {2}'.format(exepath, options, path)
        logger.debug(command)
        os.system(command)
    else:
        os.system("start notepad {0}".format(path))


def Open(file=""):
    from pyrevit import HOST_APP

    revit_ver = HOST_APP.version

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
        path = os.path.expandvars(
            "%APPDATA%\\Autodesk\\Revit\\Autodesk Revit {0}\\Revit.ini".format(
                revit_ver
            )
        )
        syntax = "-lini"
    elif file == "default revit.ini":
        # get default revit.ini file path
        path = os.path.expandvars(
            "%ALLUSERSPROFILE%\\Autodesk\\RVT {0}\\UserDataCache\\Revit.ini".format(
                revit_ver
            )
        )
        syntax = "-lini"
    elif file == "keyboard shortcuts":
        # get keyboard shortcuts file path
        path = os.path.expandvars(
            "%APPDATA%\\Autodesk\\Revit\\Autodesk Revit {0}\\KeyboardShortcuts.xml".format(
                revit_ver
            )
        )
        syntax = "-lxml"
    if file == "dynamo settings":
        # get dynamo settings file path
        path = os.getenv("APPDATA") + "\\Dynamo\\Dynamo Revit\\"
        path += dynamoVerList[HOST_APP.subversion] + "\\DynamoSettings.xml"
        syntax = "-lxml"
    elif file == "revit server settings":
        # get revit server settings file path
        path = os.path.expandvars(
            "%PROGRAMDATA%\\Autodesk\\Revit Server {0}\\Config\\RSN.ini".format(
                revit_ver
            )
        )
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
    # - C:\Users\username\AppData\Roaming\Autodesk\Revit\Autodesk Revit 2021\RevitUILayout.xml
    # - Analytic Construction file
    # - Uniformat Classifications
    # - pat files
    else:
        path = ""
        syntax = ""
    # open Notepad(++) with file
    OpenNpp(path=path, options=syntax)


def Export(file=""):
    from pyrevit import forms
    import random

    text = ""
    encoding = "utf_8"

    # get values
    if file == "formula":
        forms.check_familydoc(exitscript=True)
        for fp in sorted(get_parameters(), key=lambda p: p["Name"].lower()):
            text += "[{}] {}\r\n".format(fp["Name"], str(fp["Type"]).upper())
            text += "{}\r\n".format(fp["Formula"]) if fp["Formula"] != "" else ""
            text += "\r\n"
        syntax = "-llisp"
    elif file == "sharedparams":
        elements = get_sharedparameters()
        groups = {}
        groupnames = []
        groupno = int(random.random() * 6) * 10 + 30
        # export list of shared parameters as "[id] name (GUID)"
        # allows Select by ID and manual delete in Revit
        for sp in sorted(elements, key=lambda sp: sp["Name"].lower()):
            text += "[{}]\t{}\t({})\r\n".format(sp["Id"], sp["Name"], sp["GUID"])
            if not sp["Group"] in groupnames:
                groupnames.append(sp["Group"])
        for g in sorted(groupnames):
            groups[g] = groupno
            groupno += 1
        # export shared parameters as shared parameter file
        # groups named by "Group parameter under" value
        # group numbers are random values > 40 to allow copy/paste into existing SP files with minimum overlap
        text += (
            "\r\n\r\n# This is a Revit shared parameter file.\r\n"
            "# Do not edit manually.\r\n"
            "*META	VERSION	MINVERSION\r\n"
            "META	2	1\r\n"
            "*GROUP	ID	NAME\r\n"
        )
        for g in sorted(groupnames):
            text += "GROUP\t{}\t{}\r\n".format(groups[g], g)
        text += "*PARAM	GUID	NAME	DATATYPE	DATACATEGORY	GROUP	VISIBLE	DESCRIPTION	USERMODIFIABLE	HIDEWHENNOVALUE\r\n"
        for sp in sorted(
            sorted(elements, key=lambda sp: sp["Name"].lower()),
            key=lambda e: e["Group"],
        ):
            text += "PARAM\t{}\t{}\t{}\t\t{}\t{}\t\t1\t{}\r\n".format(
                sp["GUID"],
                sp["Name"],
                str(sp["Type"]).upper(),
                groups[sp["Group"]],
                1 if sp["Visible"] else 0,
                1 if sp["HideWhenNoValue"] else 0,
            )
        text += "\r\n"
        syntax = "-lprops"
    elif file == "familyparams":
        elements = sorted(get_loadedfamilyparameters(), key=lambda k: k["Name"])
        for fp in elements:
            text += "[{}]\r\n".format(fp["Name"])
            for p in sorted(fp["Parameters"], key=lambda k: k["Name"]):
                text += "{}\t({})\r\n".format(
                    p["Name"],
                    p["GUID"],
                )
        text += "\r\n"
        syntax = "-lprops"
    elif file == "projectparams":
        elements = sorted(get_projectparameters(), key=lambda k: k["Name"])
        for pp in elements:
            text += "[{}]\t{}\t{}\t{}\t{}\t({})\r\n".format(
                pp["Id"],
                pp["Name"],
                pp["Type"],
                pp["Group"],
                pp["Type or Instance"],
                shorten(", ".join(pp["Categories"]), width=100, placeholder="…"),
            )
        text += "\r\n"
        syntax = "-lprops"
    elif file == "fillpatterns":
        for fp in get_fillpatterns():
            text += fp + "\r\n"
        syntax = "-lprops"
    elif file == "keynotes":
        for kn in sorted(get_keynotes(), key=lambda k: k["Key"]):
            text += "{}\t{}\t{}\r\n".format(kn["Key"], kn["Text"], kn["ParentKey"])
        syntax = "-lprops"
    elif file == "typecatalog":
        # text = "," + ",".join(sorted(get_typecatalog(), key=lambda k: k["Name"])["TypeCatalogString"]).
        text = ","
        header, body = get_typecatalog()
        for tc in header:
            if tc["HasTypeValues"] == True:
                text += tc["TypeCatalogString"] + ","
            # text += str(tc) + "\r\n"
        text = text[:-1] + "\r\n"
        for tc in body:
            text += tc + "\r\n"
        syntax = ""
        encoding = "utf_16"
    # elif file == "schedule":
    # # probably not useful if can't get at formulas ???
    # # is a schedule selected or is the current view a schedule?
    # # could be multiple schedules selected - should make it so can iterate through them all?
    # # ViewSchedule.Export(folder, name, options)
    # #  ViewScheduleExportOptions()
    # # ScheduleSheetInstance
    # # ViewSchedule
    # #  Name
    # #  Definition...
    # # ScheduleDefinition
    # #  GetFilters
    # #  GetSortGroupFields
    # #  GetFields...
    # # ScheduleField
    # #  FieldType - Formula/Instance/Type
    # #  IsHidden
    # #  SheetColumnWidth
    # #  ColumnHeading
    # #  GetName
    # #  FieldIndex
    # #  ToString
    # # need to add schedule to docname
    # schedulename = "bob"
    # file = "".join( x for x in schedulename if (x.isalnum() or x in "._- ()")) # toCADname but add Upper argument
    # syntax = "-lprops"
    # Other ideas...
    # - All text on sheet, view, project
    # - Python from Dynamo
    #    C:\Users\mwarwick\AppData\Local\dynamoplayer-2\User data\dynamoplayerinstance 1\Default\Preferences
    #    "selectfile":{"last_directory":"C:\\Users\\..."}
    #    <PythonNodeModels.PythonNode ... nickname="..." ...
    #    <Script>...</script>
    else:
        syntax = ""
    # save file
    if text != "":
        docname = __revit__.ActiveUIDocument.Document.Title
        if any([x in docname for x in [".rfa", ".rvt"]]):
            docname = docname[: max(docname.rfind(".rfa"), docname.rfind(".rvt"))]
        docname += "_" + file
        path = script.get_instance_data_file(docname)
        if path:
            # tempfile = revit.files.write_text(path, text)
            # revit.files.correct_text_encoding(path)
            with codecs.open(path, "w", encoding=encoding) as text_file:
                text_file.write(text)
        # open file
        OpenNpp(path=path, options=syntax)


def try_or(fn, default=None):
    try:
        return fn()
    except:
        return default


def to_mm(num):
    return num * 304.8


def shorten(text, width=80, placeholder="…"):
    text = (text[: (width - 1)] + placeholder) if len(text) > width else text
    return text


def toCADname(name):
    name = str(name).strip(" _-$").upper()
    name = "".join(c for c in name if c.isalnum())
    return name[:31]


def get_parameters():
    # get list of parameters to be exported
    from pyrevit import DB

    fm = revit.doc.FamilyManager
    params = []

    for pr in fm.GetParameters():
        pr_def = pr.Definition
        if HOST_APP.is_newer_than(2022):
            t = pr_def.GetDataType()
            pr_type = DB.LabelUtils.GetLabelForSpec(t).replace("/", "")
        else:
            pr_type = pr_def.ParameterType
            if str(pr_type) == "Invalid":
                pr_type = "Built-in"
        params.append(
            {
                "Name": pr_def.Name,
                "isDeterminedByFormula": pr.IsDeterminedByFormula,
                "Formula": pr.Formula or "",
                "Type": pr_type,
                "isShared": pr.IsShared,
                "GUID": try_or(lambda: pr.GUID, ""),
                "Parameter": pr,
            }
        )
    return params

    # Other parameter properties:
    #
    # pgroup.append(param.Definition.ParameterGroup)
    # try: dutype.append(param.DisplayUnitType)
    # except: dutype.append(None)
    # stype.append(param.StorageType)
    # isinstance.append(param.IsInstance)
    # isreporting.append(param.IsReporting)
    # isreadonly.append(param.IsReadOnly)
    # usermodifiable.append(param.UserModifiable)
    # assocparams = param.AssociatedParameters
    # associatedparams.append(assocparams)
    # assocelems = list()
    # for assoc in assocparams:
    # assocelems.append(assoc.Element)
    # associatedelements.append(assocelems)
    # canassignformula.append(param.CanAssignFormula)


def get_sharedparameters():
    # get shared parameters from project
    from pyrevit import DB

    doc = revit.doc
    sharedparams = []

    sp_collector = (
        DB.FilteredElementCollector(doc)
        .WhereElementIsNotElementType()
        .OfClass(DB.SharedParameterElement)
    )

    for sp in sp_collector:
        sp_def = sp.GetDefinition()
        if HOST_APP.is_newer_than(2022):
            t = sp_def.GetDataType()
            sp_type = DB.LabelUtils.GetLabelForSpec(t).replace("/", "")
        else:
            sp_type = sp_def.ParameterType
        sharedparams.append(
            {
                "Name": sp.Name,
                "Id": sp.Id,
                "GUID": sp.GuidValue,
                "Group": str(sp_def.ParameterGroup)
                .replace("PG_", "")
                .replace("INVALID", "OTHER")
                .replace("AELECTRICAL", "ELECTRICAL")
                .replace("ADSK_", "")
                .replace("_", " ")
                .title(),
                "Type": sp_type,
                "Visible": sp_def.Visible,
                "HideWhenNoValue": sp.ShouldHideWhenNoValue(),
            }
        )
    return sharedparams


def get_loadedfamilyparameters():
    # get shared parameters from families loaded into the project
    from pyrevit import DB

    # Retrieve current document
    doc = revit.doc

    # Retrieve all families in current doc
    families = DB.FilteredElementCollector(doc).OfClass(DB.Family)

    # Filter the editable families and output result
    fmparams = []

    # examine each family
    for f in families:
        # only look at loadable familes
        if f.IsEditable:
            pa = []
            fi = []
            # get types
            fs = f.GetFamilySymbolIds()
            insts = False
            # get type parameters
            for t in fs:
                s = doc.GetElement(t)
                fp = s.GetOrderedParameters()
                if not insts:
                    # check if there are placed instances
                    filter = DB.FamilyInstanceFilter(doc, t)
                    fam_insts = (
                        DB.FilteredElementCollector(doc)
                        .WherePasses(filter)
                        .ToElements()
                    )
                    # if so get the instance parameters
                    if len(fam_insts) > 0:
                        insts = True
                        for i in fam_insts:
                            fi = i.Parameters
            if insts:
                # filter for shared only
                for p in fp:
                    if p.IsShared:
                        pa.append(
                            {
                                "Name": p.Definition.Name,
                                "GUID": p.GUID,
                            }
                        )
            else:
                famDoc = doc.EditFamily(f)
                fi = famDoc.FamilyManager.Parameters
            for p in fi:
                # filter for shared only
                if p.IsShared:
                    pa.append(
                        {
                            "Name": p.Definition.Name,
                            "GUID": p.GUID,
                        }
                    )
            if not insts:
                famDoc.Close(False)
            # if parameters exist add to list
            if len(pa) > 0:
                fmparams.append({"Name": f.Name, "Parameters": pa})
    return fmparams


def get_projectparameters():
    # get list of project parameters from current document
    doc = revit.doc
    projectparams = []

    parambindings = doc.ParameterBindings.ForwardIterator()

    while parambindings.MoveNext():
        cats = []
        for p in parambindings.Current.Categories:
            cats.append(p.Name)
        if HOST_APP.is_newer_than(2022):
            t = parambindings.Key.GetDataType()
            pp_type = DB.LabelUtils.GetLabelForSpec(t).replace("/", "")
        else:
            pp_type = str(parambindings.Key.ParameterType)
            if pp_type == "Invalid":
                pp_type = "Built-in"
        projectparams.append(
            {
                "Name": parambindings.Key.Name,
                "Id": parambindings.Key.Id,
                "Type": pp_type,
                "Group": str(parambindings.Key.ParameterGroup).replace("PG_", ""),
                "Type or Instance": parambindings.Current.GetType().Name[:-7],
                "Categories": cats,
            }
        )
    return projectparams


def get_typecatalog():
    # get type catalog values from family document
    from pyrevit import DB

    fm = revit.doc.FamilyManager
    u = DB.Units(DB.UnitSystem.Metric)
    tcTypes = []
    fp = get_parameters()
    fp.sort(key=lambda k: k["Name"])
    for i, p in enumerate(fp):
        if p["isDeterminedByFormula"] == False:
            ut = p["Parameter"].Definition.UnitType
            fo = u.GetFormatOptions(ut)
            s1 = DB.UnitUtils.GetTypeCatalogString(ut)
            s2 = DB.UnitUtils.GetTypeCatalogString(fo.DisplayUnits)
            if s1 == "NUMBER" and s2 == "GENERAL":
                s1 = "OTHER"
                s2 = ""
            fp[i]["TypeCatalogString"] = p["Name"] + "##" + s1 + "##" + s2
    text = ""
    for i, pa in enumerate(fp):
        hasVal = False
        if pa["isDeterminedByFormula"] == False:
            for ft in fm.Types:
                if ft.HasValue(pa["Parameter"]):
                    hasVal = True
        fp[i]["HasTypeValues"] = hasVal
    for ft in fm.Types:
        name = ft.Name
        text = name
        for i, pa in enumerate(fp):
            if pa["HasTypeValues"] == True:
                p = pa["Parameter"]
                val = ""
                if ft.HasValue(pa["Parameter"]):
                    val = ft.AsValueString(p)
                    if p.StorageType == DB.StorageType.String:
                        val = '"{}"'.format(ft.AsString(p))
                        if val == '""':
                            val = ""
                    elif p.StorageType == DB.StorageType.ElementId:
                        pid = ft.AsElementId(p)
                        ele = revit.doc.GetElement(pid)
                        fName = ele.Family.Name
                        eName = DB.Element.Name.__get__(ele)
                        val = '"{} : {}"'.format(fName, eName)
                    elif p.StorageType == DB.StorageType.Integer:
                        val = str(ft.AsInteger(p))
                    elif val is None and p.StorageType == DB.StorageType.Double:
                        val = str(ft.AsDouble(p))
                text += "," + val
        tcTypes.append(text)
    return fp, tcTypes


def get_fillpatterns():
    # get fill patterns from project and convert to .pat format
    from pyrevit import DB
    import math

    doc = revit.doc
    result = []

    # header
    result.append(";%UNITS=MM")
    result.append(";%VERSION=3.0")
    result.append(";;Exported by pyMAW, based on script by Sean Page 2022")
    result.append(
        ";;https://forum.dynamobim.com/t/export-fill-pattern-pat-file-from-revit/83014"
    )
    result.append(";;")

    fp_collector = (
        DB.FilteredElementCollector(doc)
        .WhereElementIsNotElementType()
        .OfClass(DB.FillPatternElement)
    )

    for fp in sorted(fp_collector, key=lambda f: f.Name):
        fp_name = fp.Name
        fp_def = fp.GetFillPattern()

        grids = fp_def.GetFillGrids()
        if not (fp_def.IsSolidFill or len(grids) == 0):
            result.append("*{}, {}".format(toCADname(fp_name), fp_name))
            result.append(";%TYPE={}".format(str(fp_def.Target).upper()))
            for grid in grids:
                segs = grid.GetSegments()
                string = "{},{},{},{},{}".format(
                    math.degrees(grid.Angle),
                    to_mm(grid.Origin[0]),
                    to_mm(grid.Origin[1]),
                    to_mm(grid.Shift),
                    to_mm(grid.Offset),
                )
                if len(segs) == 0:
                    string += ",0.0,0.0"
                elif len(segs) == 2:
                    string += ",{},-{}".format(to_mm(segs[0]), to_mm(segs[1]))
                else:
                    string += ",{},{}".format(to_mm(segs[0]), to_mm(segs[1]))
                result.append(string)
            result.append(";;")
    return result


def get_keynotes():
    # get keynotes from project
    from pyrevit import DB

    doc = revit.doc
    keynotes = []

    keynotetable = DB.KeynoteTable.GetKeynoteTable(doc)
    keynotelist = keynotetable.GetKeyBasedTreeEntries()
    for x in keynotelist:
        keynotes.append({"Key": x.Key, "ParentKey": x.ParentKey, "Text": x.KeynoteText})
    return keynotes
