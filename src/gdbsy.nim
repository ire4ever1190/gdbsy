{.used.}

import std/[paths, os]

proc includeGDBScript(file: static[Path]) =
  const tmp = $file
  asm """
  .pushsection ".debug_gdb_scripts", "MS",@progbits,1
  .byte 1 /* Python */
  .asciz "`tmp`"
  .popsection
  """

# Include the pretty printers shipped with the compiler
const upstreamScript = Path(getCurrentCompilerExe()) / Path"../.." / Path"tools/debug/nim-gdb.py"
includeGDBScript upstreamScript

# Include our extra snippets
const extras = Path(currentSourcePath()).parentDir() / Path"gdbsy.py"
includeGDBScript extras

