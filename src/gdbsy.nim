{.used.}

import std/[paths, os, strutils, strformat, macros]

macro includeGDBScripts(files: static[seq[Path]]): untyped =
  # Generate the list of null terminated paths

  var sectionRows = newSeq[string]()
  for file in files:
    sectionRows &= ".byte 1" # Python
    sectionRows &= ".asciz \"" & $file & "\""
  let allEntries = sectionRows.join("\n")
  let asmCode = fmt"""
.pushsection ".debug_gdb_scripts", "MS",@progbits,1
{allEntries}
.popsection
"""
  return nnkAsmStmt.newTree(newEmptyNode(), newLit asmCode)

# Include the pretty printers shipped with the compiler
const upstreamScript = Path(getCurrentCompilerExe()) / Path"../.." / Path"tools/debug/nim-gdb.py"

# Include our extra snippets
const extras = Path(currentSourcePath()).parentDir() / Path"gdbsy.py"

includeGDBScripts @[
  upstreamScript,
  extras,
]
