# import os
from pyrevit import forms
from pyrevit import script


cfg = script.get_config("Notepad++")
rs_export_format = cfg.get_option("cc_export_format", "not set")

options = ["List", "Batch", "csv"]
msg = "Current format is {}\nFormat to export:\n".format(rs_export_format)

update = forms.alert(
    msg,
    options=options,
    title="Configure Collaboration Cloud Cache Export Options",
    warn_icon=False,
    exitscript=True,
)

cfg.rs_export_format = update
script.save_config()
