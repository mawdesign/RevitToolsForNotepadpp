import re

original_string = ""
new_string = ""
indent_level = 0
extra_len = 0
indent = "\t"
quotes = []
isSelection = False

# Input:
# if(test statement, if(and(one, two, three), "and true", if(another conditional test, "all true, really", "alternative")), "otherwise")
#
# Output:
# if(
# 	test statement,
# 	if(
# 		and(
# 			one,
# 			two,
# 			three
# 		),
# 		"and true",
# 		if(
# 			another conditional test,
# 			"all true, really",
# 			"alternative"
# 		)
# 	),
# 	"otherwise"
# )

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
    return "{t[" + str(len(quotes) - 1) + "]}"


new_string = re.sub(r"\".+?\"", quote_sub, original_string)

# add returns
new_string = re.sub(r",", ",\n", new_string)
new_string = re.sub(r"\(", "(\n", new_string)
new_string = re.sub(r"\)", "\n)\n", new_string)
new_string = re.sub(r"\n\s+", "\n", new_string)
new_string = re.sub(r"\)\n,", "),", new_string)

# indent
pos = 0
extra_len = 0
next_indent_inc = 0
for st in re.finditer("\n", new_string + "\n"):
    # parse indent level
    # ')' and ',' apply to current line
    # '(' applies from next line on
    match new_string[st.start() - 1 + extra_len]:
        case "(":
            indent_level += next_indent_inc + 0
            next_indent_inc = 1
        case ")":
            indent_level += next_indent_inc - 1
            next_indent_inc = 0
        case ",":
            if new_string[st.start() - 2 + extra_len] == ")":
                indent_level -= 1
            indent_level += next_indent_inc
            next_indent_inc = 0
        case _:
            indent_level += next_indent_inc
            next_indent_inc = 0
    # apply indent to start of current line
    new_string = new_string[:pos] + indent * indent_level + new_string[pos:]
    extra_len += len(indent) * indent_level
    pos = st.end() + extra_len

# restore strings
new_string = new_string.format(t=quotes)

# output
editor.beginUndoAction()
if isSelection:
    editor.replaceSel(new_string)
else:
    editor.replaceWholeLine(lineNo, new_string)
editor.endUndoAction()
