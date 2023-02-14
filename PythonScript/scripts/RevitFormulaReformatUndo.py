import re

original_string = ""
new_string = ""
# indent_level = 0
# extra_len = 0
# indent = "\t"
quotes = []
isSelection = False

# Input:
# if(
#	test statement,
#	if(
#		and(
#			one,
#			two,
#			three
#		),
#		"and true",
#		if(
#			another conditional test,
#			"all true, really",
#			"alternative"
#		)
#	),
#	"otherwise"
# )
#
# Output:
# if( test statement, if( and( one, two, three ), "and true", if( another conditional test, "all true, really", "alternative" ) ), "otherwise" )

# input
lineNo = editor.lineFromPosition(editor.getCurrentPos())
isSelection = not editor.getSelectionEmpty()
if isSelection:
    original_string = editor.getSelText()
else:
    editor.home()
    original_string = editor.getLine(lineNo)

# pop quoted strings out
def quote_sub(match):
    global quotes
    quotes.append(match[0])
    return "{t[" + str(len(quotes)-1) + "]}"
new_string = re.sub(r"\".+?\"", quote_sub, original_string)

# remove returns, tabs, and surplus whitespace
new_string = re.sub(r",\n", ",", new_string)
new_string = re.sub(r"\(\n", "(", new_string)
new_string = re.sub(r"\n\)\n", ")", new_string)
new_string = re.sub(r"\n\s+", " ", new_string)
new_string = re.sub(r"\)\n", ")", new_string)
new_string = re.sub(r"\s+", " ", new_string)

# restore strings
new_string = new_string.format(t=quotes)

# output
editor.beginUndoAction()
if isSelection:
    editor.replaceSel(new_string)
else:
    editor.replaceWholeLine(lineNo, new_string)
editor.endUndoAction()
