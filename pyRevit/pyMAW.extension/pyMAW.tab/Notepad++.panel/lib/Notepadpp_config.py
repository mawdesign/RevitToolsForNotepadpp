import os
from pyrevit import forms
from pyrevit import script


def config():
    # get current path
    cfg = script.get_config("Notepad++")
    curexepath = cfg.get_option("notepadpath", "not set")
    if curexepath is None:
        curexepath = "not set"
    exists = os.path.exists(curexepath)

    # present option to change
    options = ["Change path", "Close"]
    msg = "Current Notepad++ location is:\n    " + curexepath + "\n"
    if not exists:
        msg = msg + "\n(File not found)\nDo you want to set it now?"
        options[0] = "Set path"
    else:
        msg = msg + "\nDo you want to change this?"
    update = forms.alert(
        msg,
        options=options,
        title="Configure Notepad++ Options",
        warn_icon=not exists,
        exitscript=True,
    )

    if update == options[0]:
        if exists:
            suggestpath = os.path.dirname(curexepath)
        elif os.path.exists(
            os.path.join(os.environ["ProgramFiles"], "Notepad++", "Notepad++.exe")
        ):
            suggestpath = os.path.join(os.environ["ProgramFiles"], "Notepad++")
        elif os.path.exists(
            os.path.join(
                os.environ.get("PortableApps.comApps", ""),
                "Notepad++Portable",
                "Notepad++Portable.exe",
            )
        ):
            suggestpath = os.path.join(
                os.environ.get("PortableApps.comApps", ""), "Notepad++Portable"
            )
        else:
            suggestpath = os.environ["ProgramFiles"]
        newexepath = forms.pick_file(
            file_ext="exe", init_dir=suggestpath, title="Select Notepad++ Executable"
        )
        cfg.notepadpath = newexepath
        script.save_config()
