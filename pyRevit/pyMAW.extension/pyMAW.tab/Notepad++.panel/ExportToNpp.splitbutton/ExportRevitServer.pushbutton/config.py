# import os
from pyrevit import forms
from pyrevit import script

# TODO:
# Add to config script
#  - rs_export_format = format, currently List,Batch, or csv
#  - add limit to specific Revit server/s
#  - add limit to specific folder/s


cfg = script.get_config("Notepad++")
rs_export_format = cfg.get_option("rs_export_format", "not set")

options = ["List", "Batch", "csv"]
msg = "Current format is {}\nFormat to export:\n".format(rs_export_format)

update = forms.alert(
    msg,
    options=options,
    title="Configure Revit Server Export Options",
    warn_icon=False,
    exitscript=True,
)

cfg.rs_export_format = update
script.save_config()
