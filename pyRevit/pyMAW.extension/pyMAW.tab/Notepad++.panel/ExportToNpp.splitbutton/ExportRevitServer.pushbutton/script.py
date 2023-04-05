from pyrevit import revit
from pyrevit import script
from pyrevit import HOST_APP
from rpws import RevitServer
from datetime import datetime
import os
import Notepadpp as npp

# TODO:
# Add to config script
#  - rs_export_format = format, currently List, Batch, or csv
#  - add limit to specific Revit server/s
#  - add limit to specific folder/s
#  - add limit to before specific date

cfg = script.get_config("Notepad++")
rs_export_format = cfg.get_option("rs_export_format", "List")
rs_export_dateafter = cfg.get_option("rs_export_dateafter", "")
if rs_export_dateafter != "":
    chk_minfo = True
else:
    chk_minfo = False
rs_export_dateafter = datetime.strptime(rs_export_dateafter, "%Y-%m-%d")

rs_servers = HOST_APP.available_servers
rs_accelerator = __revit__.Application.CurrentRevitServerAccelerator
revit_server_ver = HOST_APP.version
revit_user = HOST_APP.username
rs_localpath = cfg.get_option("rs_localpath", "C:\\RevitServerExport")
curr_folder_name = ""
text = ""

if rs_export_format == "Batch":
    preable_text = """@echo off
setlocal
"""
    server_text = """
set caduser={rs_user}
set revitserver=-s {rs_server}
set accelerator=-a {rs_accelerator}

"""
    folder_text = """
set revitserverpath={rs_folder}
set revitlocalpath={rs_localpath}\\_%revitserverpath%

echo Updating local files {count}/[[f_total]] from %revitserver%\\%revitserverpath% to %revitlocalpath% as %caduser%, via accelerator %accelerator%
echo.
"""
    model_text = """

set modelname={rs_model}
echo updating {count}/{total} %revitlocalpath%\\{rs_model}
"C:\\Program Files\Autodesk\\Revit {rs_ver}\\RevitServerToolCommand\RevitServerTool.exe" createLocalRVT "%revitserverpath%\\%modelname%" %revitserver% %accelerator% -d "%revitlocalpath%\\%modelname%" -o
"""
    syntax = "-lbatch"
elif rs_export_format == "csv":
    preable_text = (
        "Version,Server,Folder,Model,Size,Date,Last Modified By,Current User\r\n"
    )
    server_text = ""
    folder_text = ""
    model_text = '{rs_ver},{rs_server},"{rs_folder}","{rs_model}",{mi_size},{mi_date},"{mi_by}","{rs_user}"\r\n'
    syntax = "-lnormal"
else:
    preable_text = ""
    server_text = "\r\n{rs_ver} - {rs_server}\r\n"
    folder_text = "{rs_folder}\r\n"
    model_text = "\t{rs_model}\r\n"
    syntax = "-lnormal"
m_count = 0
f_count = 0
m_info = {"mi_date": "", "mi_by": "", "mi_size": ""}
text += preable_text.format(
    rs_accelerator=rs_accelerator,
    rs_ver=revit_server_ver,
    rs_user=revit_user,
    rs_localpath=rs_localpath,
)

for revit_server_name in rs_servers:
    rs = RevitServer(revit_server_name, revit_server_ver)
    text += server_text.format(
        rs_server=revit_server_name,
        rs_accelerator=rs_accelerator,
        rs_ver=revit_server_ver,
        rs_user=revit_user,
        rs_localpath=rs_localpath,
    )

    for parent, folders, files, models in rs.walk():
        m_count = 0
        for m in models:
            include = True
            m_count += 1
            model_name = m.name
            folder_name = m.path[1 : m.path.rfind("\\")]
            if rs_export_format == "csv" or chk_minfo:
                model_info = rs.getmodelinfo(m.path)
                m_info = {
                    "mi_date": model_info.date_modified,
                    "mi_by": model_info.last_modified_by,
                    "mi_size": model_info.size,
                }
            if rs_export_format == "Batch":
                model_name = model_name.replace("&", "^&")
                folder_name = folder_name.replace("&", "^&")
            if folder_name != curr_folder_name:
                f_count += 1
                curr_folder_text = folder_text.format(
                    rs_server=revit_server_name,
                    rs_accelerator=rs_accelerator,
                    rs_ver=revit_server_ver,
                    rs_user=revit_user,
                    rs_localpath=rs_localpath,
                    rs_folder=folder_name,
                    rs_model=model_name,
                    count=f_count,
                    **m_info
                )
                curr_folder_name = folder_name
            if rs_export_dateafter != "" and rs_export_dateafter > m_info["mi_date"]:
                include = False
            if include:
                text += curr_folder_text + model_text.format(
                    rs_server=revit_server_name,
                    rs_accelerator=rs_accelerator,
                    rs_ver=revit_server_ver,
                    rs_user=revit_user,
                    rs_localpath=rs_localpath,
                    rs_folder=folder_name,
                    rs_model=model_name,
                    count=m_count,
                    total=len(models),
                    **m_info
                )
                curr_folder_text = ""
if text != "":
    docname = "RevitServerExport_{}_{}".format(rs_export_format, revit_server_ver)
    text = text.replace("[[f_total]]", str(f_count))
    path = script.get_instance_data_file(docname)
    if path:
        tempfile = revit.files.write_text(path, text)
        revit.files.correct_text_encoding(path)

        # open file
        npp.OpenNpp(path=path, options=syntax)
# print(text)
