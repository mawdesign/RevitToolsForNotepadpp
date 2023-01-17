# Revit Formulas for "everyday" usage
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
from idlelib.tooltip import Hovertip
import webbrowser

params = {}
userParams = set()
lineNo = 0
totalLines = editor.getLineCount()
scriptPath = os.path.dirname(__file__)
placesList = [1000, 500, 100, 50, 10, 5, 1, 0.5, 0.1, 0.01]
unitsList = ["mm", "m", "cm", "m²", "m³", "\'", "\""]
roundFuncs = ["Round", "RoundUp", "RoundDown"]

trigFormulas = {
    "∡A" : {
        "ab" : "atan({0} / {1})",
        "ac" : "asin({0} / {1})",
        "bc" : "acos({0} / {1})",
        "a∡B" : "90° - {1}",
        "b∡B" : "90° - {1}",
        "c∡B" : "90° - {1}" },
    "∡B" : {
        "ab" : "atan({1} / {0})",
        "ac" : "acos({0} / {1})",
        "bc" : "asin({0} / {1})",
        "a∡A" : "90° - {1}",
        "b∡A" : "90° - {1}",
        "c∡A" : "90° - {1}" }, 
    "a" : {
        "bc" : "sqrt({1}^2 - {0}^2)",
        "b∡A" : "{0} * tan({1})",
        "b∡B" : "{0} / tan({1})",
        "c∡A" : "{0} * sin({1})",
        "c∡B" : "{0} * cos({1})"},
    "b" : {
        "ac" : "sqrt({1}^2 - {0}^2)",
        "a∡A" : "{0} / tan({1})",
        "a∡B" : "{0} * tan({1})",
        "c∡A" : "{0} * cos({1})",
        "c∡B" : "{0} * sin({1})"},
    "c" : {
        "ab" : "sqrt({0}^2 + {1}^2)",
        "a∡A" : "{0} / sin({1})",
        "a∡B" : "{0} / cos({1})",
        "b∡A" : "{0} / cos({1})",
        "b∡B" : "{0} / sin({1})"},
    }
trigVariables = list(trigFormulas.keys())
#["∡A", "∡B", "a", "b", "c"]

# Max / Min formulas:
# Return Length = if(A > D, if(A > C, if(A > B, A, B), if(B > C, B, C)), if(B > D, if(B > C, B, C), if(C > D, C, D)))
# Credit to: Ekkonap who posted this on May 23rd 2011.
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
    close = True
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
                close = False
        case "Other":
            formulaType = fType.get()
            if formulaType == "Range":
                fLine = "if ({0} < {1}, {1}, if ({0} > {2}, {2}, {0}))".format(miscRangeVal.get(), miscRangeMin.get(), miscRangeMax.get())
            elif formulaType in roundFuncs:
                rounding = str(miscRoundTo.get())
                units = miscRoundUnits.get()
                if len(rounding) == 0 and len(units) > 0:
                    rounding = "1"
                if len(units) > 0:
                    fLine = "{0}({1} / {2}{3}) * {2}{3}".format(formulaType.lower(), miscRoundVal.get(), rounding, units)
                elif len(rounding) > 0:
                    fLine = "{0}({1} / {2}) * {2}".format(formulaType.lower(), miscRoundVal.get(), rounding)
                else:
                    fLine = "{0}({1})".format(formulaType.lower(), miscRoundVal.get())
            else:
                messagebox.showerror(title="Not defined", message="No function for that option\n{1} Tab\nOption {0}".format(fType.get(), currentTab))
                close = False
        case _:
            messagebox.showerror(title="Not defined", message="No function for that option\n{1} Tab\nOption {0}".format(fType.get(), currentTab))
    
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
    if close:
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
    
def setTypeFilter (*args):
    global fParamsFilter, filterParams, fParams, userParams
    global miscRangeMin_combo, miscRangeVal_combo, miscRangeMax_combo, miscRoundVal_combo
    types = fParamsFilter.get()
    if types == '<show all>':
        types = []
    fParams.set(list(userParams) + filterParams(types))
    miscRangeMin_combo['values'] = list(userParams) + filterParams(types)
    miscRangeVal_combo['values'] = list(userParams) + filterParams(types)
    miscRangeMax_combo['values'] = list(userParams) + filterParams(types)
    miscRoundVal_combo['values'] = list(userParams) + filterParams(types)

def addParam(*args):
    global fParamsAdd, fParams_list, userParams
    userParams.update([fParamsAdd.get()])
    # messagebox.showerror(str(userParams))
    setTypeFilter()
    fParamsAdd.set("")

def setFType(val, unless = []):
    global fType
    curType = fType.get()
    if len(curType) == 0 or curType not in unless:
        fType.set(val)
    return True

def setTrigParams (*args):
    global trigKnown1param, trigKnown1param_combo, trigKnown2param, trigKnown1var, trigKnown2var
    trigKnown1param_combo['values'] = filterParams('ANGLE' if trigKnown1var.get()[0] == '∡' else 'LENGTH')
    if trigKnown1param.get() in filterParams('LENGTH' if trigKnown1var.get()[0] == '∡' else 'ANGLE'):
        trigKnown1param.set("")
    trigKnown2param_combo['values'] = filterParams('ANGLE' if trigKnown2var.get()[0] == '∡' else 'LENGTH')
    if trigKnown2param.get() in filterParams('LENGTH' if trigKnown2var.get()[0] == '∡' else 'ANGLE'):
        trigKnown2param.set("")

def revitFormulasForEverydayUse():
    webbrowser.open("https://www.revitforum.org/node/1126")

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
root.resizable(True, True)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
ttk.Sizegrip(root).grid(column=2, row=1, sticky=(S,E))

buildTabs = ttk.Notebook(root)
buildTabs.grid(column=0, row=0, columnspan=4, sticky=(N, W, E, S), padx=5, pady=5)
buildTabs.enable_traversal()

# Comparison Tab
compareFrame = ttk.Frame(buildTabs, padding="3 3 6 6")
compareFrame.grid(column=0, row=0, sticky=(N, W, E, S))
buildTabs.add(compareFrame, text='Comparison', underline=0)

# - Formulas
fType = StringVar()
fType_1 = ttk.Radiobutton(compareFrame, text='Minimum', variable=fType, value='<')
fType_2 = ttk.Radiobutton(compareFrame, text='Maximum', variable=fType, value='>')
fType_3 = ttk.Radiobutton(compareFrame, text='Average', variable=fType, value='avg')
fType_1.grid(column=0, row=1, sticky=(W,E))
fType_2.grid(column=0, row=2, sticky=(W,E))
fType_3.grid(column=0, row=3, sticky=(W,E))
ttk.Label(compareFrame, text="Formula").grid(column=0, row=0, sticky=W)

# - Parameters Selection
fParams = StringVar(value=filterParams())
fParamsScrollbar = Scrollbar(compareFrame, orient="vertical")
fParams_list = Listbox(compareFrame, width=25, listvariable=fParams, selectmode="extended", yscrollcommand=fParamsScrollbar.set)
fParams_list.grid(column=1, row=1, rowspan=6, sticky=(W, E, N, S))
fParamsScrollbar.config(command=fParams_list.yview)
fParamsScrollbar.grid(row=1, column=2, rowspan=6, sticky="ns")
compareFrame.grid_rowconfigure(6, weight=1)
compareFrame.grid_columnconfigure(1, weight=1)
ttk.Label(compareFrame, text="Parameters").grid(column=1, row=0, sticky=W)
fParamsAdd = StringVar()
fParamsAdd_input = ttk.Entry(compareFrame, textvariable=fParamsAdd)
fParamsAdd_input.grid(row=7, column=1, sticky="ew")
ttk.Button(compareFrame, text="+", width=2, command=addParam).grid(row=7, column=2, sticky="ew")

# Trig Tab
trigFrame = ttk.Frame(buildTabs, padding="3 3 6 6")
trigFrame.grid(column=0, row=0, sticky=(N, W, E, S))
buildTabs.add(trigFrame, text='Trigonometry', underline=0)
trigFrame.grid_rowconfigure(1, weight=1)
trigFrame.grid_columnconfigure(3, weight=1)

# - image
trigImageSrc = tk.PhotoImage(file=scriptPath + "/trig.png")
try:
    ttk.Label(trigFrame, image=trigImageSrc).grid(column=1, row=1, columnspan=3)
except:
    ttk.Label(trigFrame, text="Triangle ABC").grid(column=1, row=1, columnspan=3)

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
trigKnown1var_combo = ttk.Combobox(trigFrame, textvariable=trigKnown1var, width=10)
trigKnown1var_combo['values'] = trigVariables
trigKnown1var_combo.grid(column=1, row=4, sticky=(W, E))
trigKnown1var.set(trigVariables[3])
ttk.Label(trigFrame, text="=").grid(column=2, row=4, sticky=W)
trigKnown1param = StringVar()
trigKnown1param_combo = ttk.Combobox(trigFrame, textvariable=trigKnown1param)
trigKnown1param_combo['values'] = filterParams('LENGTH')
trigKnown1param_combo.grid(column=3, row=4, sticky=(W, E))
trigKnown1var_combo.bind("<<ComboboxSelected>>", setTrigParams)

# - known 2
trigKnown2var = StringVar()
trigKnown2var_combo = ttk.Combobox(trigFrame, textvariable=trigKnown2var, width=10)
trigKnown2var_combo['values'] = trigVariables
trigKnown2var_combo.grid(column=1, row=5, sticky=(W, E))
trigKnown2var.set(trigVariables[4])
ttk.Label(trigFrame, text="=").grid(column=2, row=5, sticky=W)
trigKnown2param = StringVar()
trigKnown2param_combo = ttk.Combobox(trigFrame, textvariable=trigKnown2param)
trigKnown2param_combo['values'] = filterParams('LENGTH')
trigKnown2param_combo.grid(column=3, row=5, sticky=(W, E))
trigKnown2var_combo.bind("<<ComboboxSelected>>", setTrigParams)

# Circle Tab
circFrame = ttk.Frame(buildTabs, padding="3 3 6 6")
circFrame.grid(column=0, row=0, sticky=(N, W, E, S))
buildTabs.add(circFrame, text='Circle', underline=1)


# Misc Tab
miscFrame = ttk.Frame(buildTabs, padding="3 3 6 6")
miscFrame.grid(column=0, row=0, sticky=(N, W, E, S))
buildTabs.add(miscFrame, text='Other', underline=0)
miscFrame.grid_columnconfigure(2, weight=1)

# - Range
fTypeValidate = root.register(setFType)
ttk.Label(miscFrame, text='Check value within allowed range:', font="-size 9 -weight bold").grid(column=0, columnspan=3, row=0, sticky=W)
miscRange = ttk.Radiobutton(miscFrame, text='Range', variable=fType, value='Range')
miscRange.grid(column=0, row=2, sticky=(W,E))
ttk.Label(miscFrame, text='Min').grid(column=1, row=1, sticky=W)
ttk.Label(miscFrame, text='Value').grid(column=1, row=2, sticky=W)
ttk.Label(miscFrame, text='Max').grid(column=1, row=3, sticky=W)
miscRangeMin = StringVar()
miscRangeMin_combo = ttk.Combobox(miscFrame, textvariable=miscRangeMin, validate='key', validatecommand=(fTypeValidate, 'Range'))
miscRangeMin_combo['values'] = filterParams()
miscRangeMin_combo.grid(column=2, row=1, sticky=(W, E), pady=2)
miscRangeMin_combo.bind("<<ComboboxSelected>>", lambda e: fType.set('Range'))
miscRangeVal = StringVar()
miscRangeVal_combo = ttk.Combobox(miscFrame, textvariable=miscRangeVal, validate='key', validatecommand=(fTypeValidate, 'Range'))
miscRangeVal_combo['values'] = filterParams()
miscRangeVal_combo.grid(column=2, row=2, sticky=(W, E), pady=2)
miscRangeVal_combo.bind("<<ComboboxSelected>>", lambda e: fType.set('Range'))
miscRangeMax = StringVar()
miscRangeMax_combo = ttk.Combobox(miscFrame, textvariable=miscRangeMax, validate='key', validatecommand=(fTypeValidate, 'Range'))
miscRangeMax_combo['values'] = filterParams()
miscRangeMax_combo.grid(column=2, row=3, sticky=(W, E), pady=2)
miscRangeMax_combo.bind("<<ComboboxSelected>>", lambda e: fType.set('Range'))

#---
ttk.Separator(miscFrame, orient="horizontal").grid(column=0, columnspan=3, row=4, sticky=(W,E))

# - Round
roundTitle = ttk.Label(miscFrame, text='Rounding:', font="-size 9 -weight bold")
roundFrame = ttk.LabelFrame(miscFrame, labelwidget=roundTitle, relief="flat", borderwidth=0)
roundFrame.grid(column=0, row=5, rowspan=5, sticky=(W,E))
miscRound = ttk.Radiobutton(roundFrame, text='Round', variable=fType, value='Round', padding="2 5 5 0")
miscRound.grid(column=0, row=0, sticky=(W,E))
ttk.Label(roundFrame, text='(x.4 → x, x.5 → x+1)', font="-size 8 -slant italic", padding="20 0 5 5").grid(column=0, row=1, sticky=W)
miscRoundUp = ttk.Radiobutton(roundFrame, text='Round Up', variable=fType, value='RoundUp', padding="2 5 5 0")
miscRoundUp.grid(column=0, row=2, sticky=(W,E))
ttk.Label(roundFrame, text='(x.y → x+1)', font="-size 8 -slant italic", padding="20 0 5 5").grid(column=0, row=3, sticky=W)
miscRoundDown = ttk.Radiobutton(roundFrame, text='Round Down', variable=fType, value='RoundDown', padding="2 5 5 0")
miscRoundDown.grid(column=0, row=4, sticky=(W,E))
ttk.Label(roundFrame, text='(x.y → x)', font="-size 8 -slant italic", padding="20 0 5 5").grid(column=0, row=5, sticky=W)
ttk.Label(miscFrame, text='Value').grid(column=1, row=6, sticky=(W,S))
ttk.Label(miscFrame, text='To').grid(column=1, row=7, sticky=W)
ttk.Label(miscFrame, text='Units').grid(column=1, row=8, sticky=(W,N))
miscRoundVal = StringVar()
miscRoundVal_combo = ttk.Combobox(miscFrame, textvariable=miscRoundVal, validate='key', validatecommand=(fTypeValidate, 'Round', roundFuncs))
miscRoundVal_combo['values'] = filterParams()
miscRoundVal_combo.grid(column=2, row=6, sticky=(W, E, S), pady=2)
miscRoundVal_combo.bind("<<ComboboxSelected>>", lambda e: fType.set('Round') if fType.get() not in roundFuncs else True)
miscRoundTo = StringVar()
miscRoundTo_combo = ttk.Combobox(miscFrame, textvariable=miscRoundTo)
miscRoundTo_combo['values'] = placesList
miscRoundTo_combo.grid(column=2, row=7, sticky=(W, E), pady=2)
miscRoundUnits = StringVar()
miscRoundUnits_combo = ttk.Combobox(miscFrame, textvariable=miscRoundUnits)
miscRoundUnits_combo['values'] = unitsList
miscRoundUnits_combo.grid(column=2, row=8, sticky=(W, E, N), pady=2)

# About Tab
aboutFrame = ttk.Frame(buildTabs, padding="3 3 6 6")
aboutFrame.grid(column=0, row=0, sticky=(N, W, E, S))
buildTabs.add(aboutFrame, text='?')
aboutLink = tk.Label(aboutFrame, text="Tools to build Revit family formulas, based on the Revit Forum post \"Revit Formulas for Everyday Use\".\r\nOriginal forum post by Munkholm\r\nTools developed by MAW Design", wraplength=200)
aboutLink.grid(column=0, row=0, sticky=(E,W))
aboutLink.bind('<Configure>', lambda e: aboutLink.config(wraplength=aboutLink.winfo_width()-10))
ttk.Button(aboutFrame, text="Open Revit Forum post", command=revitFormulasForEverydayUse).grid(column=0, row=1, padx=5, pady=2)
aboutFrame.grid_rowconfigure(0, weight=1)
aboutFrame.grid_columnconfigure(0, weight=1)

# Filter + Buttons
fParamsImageSrc = tk.PhotoImage(file=scriptPath + "/filter.png")
try:
    ttk.Label(root, image=fParamsImageSrc).grid(column=0, row=1)
except:
    ttk.Label(trigFrame, text="Filter").grid(column=0, row=1)
fParamsFilter = StringVar()
fParamsFilter_list = ttk.Combobox(root, width=16, textvariable=fParamsFilter, state="readonly")
fParamsFilter_list['values'] = ['<show all>'] + sorted(set(params.values()))
fParamsFilter.set(fParamsFilter_list['values'][0])
fParamsFilter_list.grid(column=1, row=1, sticky=(W,E), padx="0 10")
fParamsFilter_list.bind("<<ComboboxSelected>>", setTypeFilter)
# ttk.Label(compareFrame, text="Parameter Type Filter:").grid(column=0, row=4, sticky=W, pady="10 0")
action = ttk.Button(root, text="Insert", default="active", command=createFormulas)
action.grid(column=2, row=1, sticky=(E), padx=5, pady=2)
ttk.Button(root, text="Close", command=closeDialog).grid(column=3, row=1, sticky=(E), padx=5, pady=2)

fType_1.focus_force()
root.bind('<Return>', lambda e: action.invoke())
root.bind('<Key-Escape>', closeDialog)

root.mainloop()
