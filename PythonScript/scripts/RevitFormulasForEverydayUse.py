# Revit Formulas for "everyday" usage
# Max / Min formulas:
# Return Length = if(A > D, if(A > C, if(A > B, A, B), if(B > C, B, C)), if(B > D, if(B > C, B, C), if(C > D, C, D)))
# Credit to: Ekkonap who posted this on May 23rd 2011.
#from tkinter import *
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
from idlelib.tooltip import Hovertip

params = {}
lineNo = 0
totalLines = editor.getLineCount()
scriptPath = os.path.dirname(__file__)

trigFormulas = {
    "∡A" : {
        "ab" : "atan({0} / {1})",
        "ac" : "asin({0} / {1})",
        "bc" : "acos({0} / {1})",
        "∡Bc" : "90° - {0}",
        "∡Ab" : "90° - {0}",
        "∡Bb" : "90° - {0}" },
    "∡B" : "", "a" : "", "b" : "", "c" : ""
    }
trigVariables = list(trigFormulas.keys())
#["∡A", "∡B", "a", "b", "c"]

def fxMinMaxAvg(i, fn = ">"):
    match fn:
        case "<" | ">":
            if len(i) == 2:
                return "if({0} {2} {1}, {0}, {1})".format(i[0], i[1], fn)
            elif len(i)  > 2:
                fx = "if({0} {2} {1}, ".format(i[0], i[-1], fn)
                fx += fxMinMaxAvg(i[ : -1], fn) + ", "
                fx += fxMinMaxAvg(i[1 : ], fn) + ")"
                return fx
            elif len(i)  == 1:
                return i[0]
        case "avg" if len(i) > 1:
            return "(" + " + ".join(i) + ") / " + str(len(i))
    return i

def createFormulas (*args):
    global params #paramSettings, paramCount, group, lastGroupLine
    # Process input
    fLine = ""
    currentTab = buildTabs.tab(buildTabs.select(), "text")
    match currentTab:
        case "Comparison":
            paramSelect = fParams_list.curselection()
            formulaType = fType.get()
            fLine = fxMinMaxAvg([fParams_list.get(i) for i in paramSelect], formulaType)
        case "Trigonometry":
            want = trigWanted.get()
            known = sorted([trigKnown1var.get(), trigKnown2var.get()])
            knownKey = "".join(sorted([trigKnown1var.get(), trigKnown2var.get()]))
            if known[0] == trigKnown1var.get():
                known1 = trigKnown1param.get()
                known2 = trigKnown2param.get()
            else:
                known1 = trigKnown2param.get()
                known2 = trigKnown1param.get()

            if knownKey in trigFormulas[want]:
                fLine = trigFormulas[want][knownKey].format(known1, known2)
            else:
                messagebox.showerror(title="No formula", message="No solution for {0} where {1} + {2} are known\r\n".format(want, trigKnown1var.get(), trigKnown2var.get()))
    
    # Process input
    if fLine != "":
        editor.beginUndoAction()
        # Write line
        editor.home()
        curPos = editor.getCurrentPos()
        editor.newLine()
        editor.insertText(curPos, fLine)
        editor.endUndoAction()
    
    # close
    root.destroy()

def closeDialog (*args):
    root.destroy()

def filterParams (types = []):
    global params
    if isinstance(types, str):
        types = [types]
    if len(types) == 0:
        types = params.values()
    return list(k for k,v in params.items() if v in types)

while lineNo < totalLines:
    line = editor.getLine(lineNo)
    if line.startswith("[") and line.find("]") > 1:
        params[line[1 : line.find("]")].strip()] = line[line.find("]") + 2 : ].strip()
    lineNo += 1

#params = {"∡A": "ANGLE", "∡B": "ANGLE", "a": "LENGTH", "b": "LENGTH", "c": "LENGTH"}

# Create dialog
root = Tk()
root.title("Build Formula")
root.attributes('-topmost',True)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

buildTabs = ttk.Notebook(root)
buildTabs.grid(column=0, row=0, columnspan=2, sticky=(N, W, E, S), padx=5, pady=5)
buildTabs.enable_traversal()

# Comparison Tab
compareFrame = ttk.Frame(buildTabs, padding="3 3 6 6")
compareFrame.grid(column=0, row=0, sticky=(N, W, E, S))
buildTabs.add(compareFrame, text='Comparison', underline=0)

# - Parameters Selection
fParams = StringVar(value=filterParams("LENGTH"))
fParams_list = Listbox(compareFrame, width=30, listvariable=fParams, selectmode="extended")
fParams_list.grid(column=2, row=2, rowspan=3, sticky=(W, E, N, S))
ttk.Label(compareFrame, text="Parameters").grid(column=2, row=1, sticky=W)

# - Formulas
fType = StringVar()
fType_1 = ttk.Radiobutton(compareFrame, text='Minimum', variable=fType, value='<')
fType_2 = ttk.Radiobutton(compareFrame, text='Maximum', variable=fType, value='>')
fType_3 = ttk.Radiobutton(compareFrame, text='Average', variable=fType, value='avg')
fType_1.grid(column=1, row=2, sticky=(W,E))
fType_2.grid(column=1, row=3, sticky=(W,E))
fType_3.grid(column=1, row=4, sticky=(W,E))
ttk.Label(compareFrame, text="Formula").grid(column=1, row=1, sticky=W)

for child in compareFrame.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

# Trig Tab
trigFrame = ttk.Frame(buildTabs, padding="3 3 6 6")
trigFrame.grid(column=0, row=0, sticky=(N, W, E, S))
buildTabs.add(trigFrame, text='Trigonometry', underline=0)

# - image
trigImageSrc = tk.PhotoImage(file=scriptPath + "/trig.png")
try:
    ttk.Label(trigFrame, image=trigImageSrc).grid(column=1, row=1, columnspan=3, sticky=W)
except:
    ttk.Label(trigFrame, text="Triangle ABC").grid(column=1, row=1, columnspan=3, sticky=W)

# - wanted
trigWanted = StringVar()
trigWanted_combo = ttk.Combobox(trigFrame, textvariable=trigWanted)
trigWanted_combo['values'] = trigVariables
trigWanted_combo.grid(column=3, row=2, sticky=(W, E))
ttk.Label(trigFrame, text="Desired value:").grid(column=1, row=2, sticky=W)
trigWanted.set(trigVariables[0])

ttk.Label(trigFrame, text="where…").grid(column=1, row=3, sticky=W)

# - known 1
trigKnown1var = StringVar()
trigKnown1_combo = ttk.Combobox(trigFrame, textvariable=trigKnown1var)
trigKnown1_combo['values'] = trigVariables
trigKnown1_combo.grid(column=1, row=4, sticky=(W, E))
trigKnown1var.set(trigVariables[3])
ttk.Label(trigFrame, text="=").grid(column=2, row=4, sticky=W)
trigKnown1param = StringVar()
trigKnown1param_combo = ttk.Combobox(trigFrame, textvariable=trigKnown1param)
trigKnown1param_combo['values'] = filterParams()
trigKnown1param_combo.grid(column=3, row=4, sticky=(W, E))
if len(trigKnown1param_combo['values']) > 0:
    trigKnown1param.set(trigKnown1param_combo['values'][0])

# - known 2
trigKnown2var = StringVar()
trigKnown2var_combo = ttk.Combobox(trigFrame, textvariable=trigKnown2var)
trigKnown2var_combo['values'] = trigVariables
trigKnown2var_combo.grid(column=1, row=5, sticky=(W, E))
trigKnown2var.set(trigVariables[4])
ttk.Label(trigFrame, text="=").grid(column=2, row=5, sticky=W)
trigKnown2param = StringVar()
trigKnown2param_combo = ttk.Combobox(trigFrame, textvariable=trigKnown2param)
trigKnown2param_combo['values'] = filterParams()
trigKnown2param_combo.grid(column=3, row=5, sticky=(W, E))
if len(trigKnown2param_combo['values']) > 0:
    trigKnown2param.set(trigKnown2param_combo['values'][0])


# Buttons
action = ttk.Button(root, text="Insert", default="active", command=createFormulas)
action.grid(column=0, row=1, sticky=(W,E), padx=5, pady=2)
ttk.Button(root, text="Close", command=closeDialog).grid(column=1, row=1, sticky=(W,E), padx=5, pady=2)

fType_1.focus_force()
root.bind('<Return>', lambda e: action.invoke())
root.bind('<Key-Escape>', closeDialog)

root.mainloop()
