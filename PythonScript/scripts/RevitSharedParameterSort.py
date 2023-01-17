# Sort Shared Parameters by Group and Name
# MAW 2022
editor.setTabWidth(12)
lineNo = 0
totalLines = editor.getLineCount()
line = ""
param = []

#function to get column to sort by
#line    = text, tab delimited
#col     = number of column to get, 0 is first column
#colType = str = text (will convert to lowercase for sorting), num = integer
def getCol(line, col, colType="str"):
    cols = line.split("\t")
    ret = cols[col]
    if colType == "num":
        ret = int(ret)
    else:
        ret = ret.lower()
    return ret

# skip preamble
while lineNo < totalLines and not line.startswith("*PARAM"):
    line = editor.getLine(lineNo)
    lineNo += 1

# get parameters
firstParamLine = lineNo
while lineNo < totalLines and editor.getLine(lineNo).startswith("PARAM"):
    line = editor.getLine(lineNo)
    param.append(line)
    lineNo += 1

# sort
# by GROUP (column 5), then NAME (column 2)
param.sort(key = lambda col: getCol(col, 2))
param.sort(key = lambda col: getCol(col, 5, "num"))

# write back
editor.beginUndoAction()
lineNo = firstParamLine
for param1 in param:
    editor.replaceWholeLine(lineNo, param1)
    lineNo += 1
editor.endUndoAction()
