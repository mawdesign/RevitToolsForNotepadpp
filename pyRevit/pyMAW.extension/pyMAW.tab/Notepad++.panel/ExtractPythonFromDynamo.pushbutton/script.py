from pyrevit import forms
from pyrevit import script
import Notepadpp as npp
import json, codecs

sourceFile = forms.pick_file(file_ext="dyn")  # init_dir=''


def vetFilename(name):
    keepCharacters = ("_", "-", " ")
    replacements = [
        (".", "_"),
        (" -", "-"),
        ("- ", "-"),
        ("---", "-"),
        ("--", "-"),
        ("___", "_"),
        ("__", "_"),
    ]
    name = " ".join(name.split())
    for sub in replacements:
        name = name.replace(sub[0], sub[1])
    name = "".join(c for c in name if c.isalnum() or c in keepCharacters)
    return name[:31]


with open(sourceFile, "r") as jsonFile:
    dynamoScript = json.load(jsonFile)
pythonScripts = [
    x for x in dynamoScript["Nodes"] if x["NodeType"] == "PythonScriptNode"
]
pythonNames = [
    x
    for x in dynamoScript["View"]["NodeViews"]
    if x["Id"] in [s["Id"] for s in pythonScripts]
]
text = "#\r\n# Scripts from {}\r\n#\r\n# Extracted using pyMAW\r\n\r\n".format(
    sourceFile
)
for s in pythonScripts:
    nodeName = "Python Script"
    for n in pythonNames:
        if n["Id"] == s["Id"]:
            nodeName = n["Name"]
            continue
    text += "''''\r\n{0}\r\n# Script from Node \"{1}\"\r\n{0}\r\n'''\r\n\r\n".format(
        "-" * 48,
        nodeName,
    )
    text += s["Code"].decode("string_escape") + "\r\n\r\n"
if text != "":
    docname = "Python from Dynamo_"
    docname += vetFilename(sourceFile[sourceFile.rfind("\\") + 1 : -4])
    path = script.get_instance_data_file(docname)
    if path:
        with codecs.open(path, "w", encoding="utf_8") as text_file:
            text_file.write(text)
    syntax = "-lpython"
    # open file

    npp.OpenNpp(targetpath=path, options=syntax)
