import std/paths

const fileLocation = Path(currentSourcePath()).parentDir() / Path"gdbsy.py"

asm """
.pushsection ".debug_gdb_scripts", "MS",@progbits,1
.byte 1 /* Python */
.asciz "`fileLocation`"
.popsection
"""
