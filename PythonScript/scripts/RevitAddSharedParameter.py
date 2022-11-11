import uuid
from tkinter import *
from tkinter import ttk
from idlelib.tooltip import Hovertip

# File format is tab delimited
# ----------------------------
# # This is a Revit shared parameter file.
# # Do not edit manually.
# *META	VERSION	MINVERSION
# META	2	1
# *GROUP	ID	NAME
# GROUP	1	Dimensions
# *PARAM	GUID	NAME	DATATYPE	DATACATEGORY	GROUP	VISIBLE	DESCRIPTION	USERMODIFIABLE	HIDEWHENNOVALUE
# PARAM	f7676631-f613-4a65-bc5e-c3166d03e2cb	Zcalc_AngleA	ANGLE		1	0		1	0

# Set variables
paramSettings = {} #{'enter' : False}
paramLine = ""
paramCount = int(1)
paramTypes = {'short' : ('ANGLE', 'AREA', 'CURRENCY', 'HVAC_FACTOR', 'IMAGE', 'INTEGER', 'LENGTH', 'MATERIAL', 'MULTILINETEXT', 'NUMBER', 'TEXT', 'URL', 'VOLUME', 'YESNO' ),\
    'full' : ('ANGLE', 'AREA', 'AREAFORCE', 'COST_PER_AREA', 'CURRENCY', 'DISTANCE', 'ELECTRICAL_APPARENT_POWER', 'ELECTRICAL_CURRENT',\
        'ELECTRICAL_FREQUENCY', 'ELECTRICAL_POTENTIAL', 'ELECTRICAL_POWER', 'ELECTRICAL_WATTAGE', 'FORCE', 'HVAC_AIR_FLOW', 'HVAC_COEFFICIENT_OF_HEAT_TRANSFER',\
        'HVAC_COOLING_LOAD', 'HVAC_DUCT_SIZE', 'HVAC_FACTOR', 'HVAC_HEATING_LOAD', 'HVAC_HEAT_GAIN', 'HVAC_PRESSURE', 'HVAC_TEMPERATURE', 'HVAC_VELOCITY',\
        'IMAGE', 'INTEGER', 'LENGTH', 'LINEARFORCE', 'MASS_DENSITY', 'MATERIAL', 'MOMENT', 'MULTILINETEXT', 'NOOFPOLES', 'NUMBER', 'PIPE_SIZE', 'PIPING_FLOW',\
        'PIPING_PRESSURE', 'PIPING_TEMPERATURE', 'ROTATION_ANGLE', 'SLOPE', 'SPEED', 'TEXT', 'TIMEINTERVAL', 'URL', 'VOLUME', 'YESNO')
}
lineNo = 0
totalLines = editor.getLineCount()
firstGroupLine = int()
lastGroupLine = int()
line = ""
group = {}

class Hovertip2(Hovertip):
    "A tooltip that pops up when a mouse hovers over an anchor widget."
    def __init__(self, anchor_widget, text, hover_delay=1000):
        """Create a text tooltip with a mouse hover delay.
        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, in milliseconds
        Note that a widget will only be shown when showtip() is called,
        e.g. after hovering over the anchor widget with the mouse for enough
        time.
        """
        super(Hovertip, self).__init__(anchor_widget, hover_delay=hover_delay)
        self.text = text

    def showcontents(self):
        label = Label(self.tipwindow, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1)
        self.tipwindow.attributes('-topmost',True)
        label.pack()

# Increments a string such as "001" -> "002" or "AA" -> "AB"
def incStr(str):
    carry = True
    ret = ""
    ascii = int()
    str = str.strip()
    for i in range(len(str),0,-1):
        ascii = ord(str[i-1])
        if carry and ascii in list(range(ord("0"),ord("9")+1)) + list(range(ord("A"),ord("Z")+1)) + list(range(ord("a"),ord("z")+1)):
            ascii += 1
            match ascii:
                case 58:  # past 9
                    ascii = 48 # 0
                case 91:  # past 'Z'
                    ascii = 65 # 'A'
                case 123: # past 'z'
                    ascii = 97 # 'a'
                case _:
                    carry = False
        ret = chr(ascii) + ret
    if carry:
        match ascii:
            case 48:  # 0
                ret = "1" + ret
            case 65:  # 'A'
                ret = "A" + ret
            case 97: # 'a'
                ret = "a" + ret
    return ret

# On Create get inputs from dialog and add shared params
def createParams (*args):
    global paramSettings, paramCount, group, lastGroupLine
    # paramSettings['enter'] = True
    paramSettings['name'] = pName.get()
    paramSettings['desc'] = pDesc.get()
    paramSettings['type'] = pType.get()
    paramSettings['groupName'] = pGroup.get()
    if paramSettings['groupName'] in group.keys():
        paramSettings['group'] = str(group[pGroup.get()])
    else:
        # add new group if groups exist
        if firstGroupLine != totalLines:
            groupNo = str(int(group[next(reversed(group))]) + 1)
            editor.replaceWholeLine(lastGroupLine, editor.getLine(lastGroupLine) + "GROUP\t" + groupNo + "\t" + paramSettings['groupName'] + "\r\n")
            paramSettings['group'] = groupNo
            group[paramSettings['groupName']] = groupNo
            pGroup_combo['values'] = list(group.keys())
            pGroup.set(paramSettings['groupName'])
            lastGroupLine += 1
        else:
            # avoid error if not shared parameter file
            paramSettings['group'] = str(next(iter(group.items()))[1])
    paramSettings['visible'] = pVisible.get()
    paramSettings['hide'] = pHide.get()
    paramSettings['suffix'] = pSuffix.get()
    paramCount = pIterate.get()
    
    # Process input
    editor.beginUndoAction()
    for i in range(paramCount):
        # Get a GUID
        newUUID = uuid.uuid4()

        # Construct line
        paramLine = "PARAM\t" + str(newUUID) + "\t" + paramSettings['name'] + paramSettings['suffix'] + "\t" + paramSettings['type'] + "\t\t" + paramSettings['group']\
        + "\t" + paramSettings['visible'] + "\t" + paramSettings['desc'] + "\t1\t" + paramSettings['hide']
        console.write(paramLine + "\r\n")
        
        # Write line
        editor.home()
        curPos = editor.getCurrentPos()
        editor.newLine()
        editor.insertText(curPos, paramLine)
        
        # Increment suffix
        paramSettings['suffix'] = incStr(paramSettings['suffix'])
    editor.endUndoAction()

def chooseTypeList (*args):
    if pType_combo['values'] == paramTypes['short']:
        pType_combo['values'] = paramTypes['full']
        pType_add.configure(text="-")
    else:
        pType_combo['values'] = paramTypes['short']
        pType_add.configure(text="+")

def closeDialog (*args):
    root.destroy()

# Get Groups
# - skip preamble
while lineNo < totalLines and not line.startswith("*GROUP"):
    line = editor.getLine(lineNo)
    lineNo += 1
# get groups
firstGroupLine = lineNo
while lineNo < totalLines and editor.getLine(lineNo).startswith("GROUP"):
    line = editor.getLine(lineNo)
    cols = line.split("\t")
    group[cols[2].strip()] = cols[1]
    lineNo += 1
lastGroupLine = lineNo - 1
groups = sorted(group.items(), key=lambda x:x[0])
if len(groups) > 0: 
    group = dict(groups)
else:
    group = { "" : 1 }

# Create dialog
root = Tk()
root.title("Create New Shared Parameter")
root.attributes('-topmost',True)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

#Parameter Name
pName = StringVar()
pName_entry = ttk.Entry(mainframe, width=30, textvariable=pName)
pName_entry.grid(column=2, row=1, columnspan=3, sticky=(W, E))
ttk.Label(mainframe, text="Name").grid(column=1, row=1, sticky=W)

#Parameter Description
pDesc = StringVar()
pDesc_entry = ttk.Entry(mainframe, width=30, textvariable=pDesc)
pDesc_entry.grid(column=2, row=2, columnspan=3, sticky=(W, E))
ttk.Label(mainframe, text="Description").grid(column=1, row=2, sticky=W)

#Parameter Type
pType_frame = ttk.Frame(mainframe, padding="0")
pType_frame.grid(column=2, row=3, sticky=(W,E))
pType = StringVar()
pType_combo = ttk.Combobox(pType_frame, textvariable=pType)
pType_combo['values'] = paramTypes['short']
pType_combo.grid(column=1, row=1, sticky=(W,E))
pType_combo.state(["readonly"])
#pType_combo.bind('<<ComboboxSelected>>', lambda e: mainframe.focus())
ttk.Label(mainframe, text="Type").grid(column=1, row=3, sticky=W)
pType.set('LENGTH')
pType_add = ttk.Button(pType_frame, text="+", width=2, command=chooseTypeList)
pType_add.grid(column=2, row=1, sticky=(W,E))
pType_tip = Hovertip2(pType_add,'Show less frequently used \nparameter types in the list', hover_delay=100)

#Parameter Group
pGroup = StringVar()
pGroup_combo = ttk.Combobox(mainframe, textvariable=pGroup)
pGroup_combo['values'] = list(group.keys())
pGroup_combo.grid(column=4, row=3, sticky=(W, E))
ttk.Label(mainframe, text="Group").grid(column=3, row=3, sticky=W)
pGroup.set(list(group.keys())[0])

#Parameter Visible/Hidden
pVisible = StringVar(value="1")
pVisible_check = ttk.Checkbutton(mainframe, text='', 
	    variable=pVisible, onvalue="1", offvalue="0")
pVisible_check.grid(column=2, row=4, sticky=(W))
ttk.Label(mainframe, text="Visible").grid(column=1, row=4, sticky=W)

#Parameter Hide When No Value
pHide = StringVar(value="0")
pHide_check = ttk.Checkbutton(mainframe, text='', 
	    variable=pHide, onvalue="1", offvalue="0")
pHide_check.grid(column=2, row=5, sticky=(W))
ttk.Label(mainframe, text="Hide when no value").grid(column=1, row=5, sticky=W)

# Number of Parameters to create
pIterate = IntVar(value=paramCount)
pIterate_spin = ttk.Spinbox(mainframe, width=5, from_=1, to=100, increment=1, textvariable=pIterate)
pIterate_spin.grid(column=4, row=4, sticky=(W))
ttk.Label(mainframe, text="Parameters to create").grid(column=3, row=4, sticky=W)

# Suffix to add
pSuffix = StringVar()
pSuffix_entry = ttk.Entry(mainframe, width=10, textvariable=pSuffix)
pSuffix_entry.grid(column=4, row=5, sticky=(W))
pSuffix_tip = Hovertip2(pSuffix_entry,'This will be added to the name and \nincremented for each new parameter', hover_delay=100)
ttk.Label(mainframe, text="Suffix").grid(column=3, row=5, sticky=W)

# Buttons
action = ttk.Button(mainframe, text="Create", default="active", command=createParams)
action.grid(column=3, row=7, sticky=(W,E))
ttk.Button(mainframe, text="Close", command=closeDialog).grid(column=4, row=7, sticky=(W,E))

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

pName_entry.focus_force()
root.bind('<Return>', lambda e: action.invoke())
root.bind('<Key-Escape>', closeDialog)

root.mainloop()
