# Mainly taken from https://github.com/nim-lang/Nim/blob/devel/tools/debug/nim-gdb.py but updated to fix some problems in GDB.
# Have not ported the fixes upstream yet since I'd need to make the code backwards compaitable (something about gdb.types not existing in newer versions?)

import gdb
from gdb import ValuePrinter
import re

def strFromLazy(strVal):
  if isinstance(strVal, str):
    return strVal
  else:
    return strVal.value().string("utf-8")

class NimStringPrinter(ValuePrinter):
  pattern = r'^(NimStringDesc \*|NimStringV2)$'

  def __init__(self, val):
    self.val = val

  def display_hint(self):
    return 'string'

  def to_string(self):
    if self.val:
      if self.val.type.name == "NimStringV2":
        l = int(self.val["len"])
        data = self.val["p"]["data"]
      else:
        l = int(self.val['Sup']['len'])
        data = self.val["data"]
      return data.lazy_string(encoding="utf-8", length=l)
    else:
      return ""

  def __str__(self):
    return strFromLazy(self.to_string())

class NimSeq:
  # Wrapper around sequences.
  # This handles the differences between old and new runtime

  def __init__(self, val):
    self.val = val
    # new runtime has sequences on stack, old has them on heap
    self.new = val.type.code != gdb.TYPE_CODE_PTR
    if self.new:
      # Some seqs are just the content and to save repeating ourselves we do
      # handle them here. Only thing that needs to check this is the len/data getters
      self.isContent = val.type.name.endswith("Content")

  def __bool__(self):
    if self.new:
      return self.val is not None
    else:
      return bool(self.val)

  def __len__(self):
    if not self:
      return 0
    if self.new:
      if self.isContent:
        return int(self.val["cap"])
      else:
        return int(self.val["len"])
    else:
      return self.val["Sup"]["len"]

  @property
  def data(self):
    if self.new:
      if self.isContent:
        return self.val["data"]
      elif self.val["p"]:
        return self.val["p"]["data"]
    else:
      return self.val["data"]

  @property
  def cap(self):
    if not self:
      return 0
    if self.new:
      if self.isContent:
        return int(self.val["cap"])
      elif self.val["p"]:
        return int(self.val["p"]["cap"])
      else:
        return 0
    return int(self.val['Sup']['reserved'])

class NimSeqPrinter(ValuePrinter):
  pattern = r'^tySequence_\w*\s?\*?$'

  def __init__(self, val):
    self.val = NimSeq(val)


  def display_hint(self):
    return 'array'

  def to_string(self):
    return f'seq({len(self.val)}, {self.val.cap})'

  def children(self):
    if self.val:
      val = self.val
      length = len(val)

      if length <= 0:
        return

      data = val.data

      inaccessible = False
      for i in range(length):
        if inaccessible:
          return
        try:
          str(data[i])
          yield "[{0}]".format(i), data[i]
        except RuntimeError:
          inaccessible = True
          yield "[{0}]".format(i), "inaccessible"

################################################################################

class NimArrayPrinter(ValuePrinter):
  pattern = r'^tyArray_\w*$'

  def __init__(self, val):
    self.val = val

  def display_hint(self):
    return 'array'

  def to_string(self):
    return 'array'

  def children(self):
    length = self.val.type.sizeof // self.val[0].type.sizeof
    align = len(str(length-1))
    for i in range(length):
      yield ("[{0:>{1}}]".format(i, align), self.val[i])

import gdb.printing

pp = gdb.printing.RegexpCollectionPrettyPrinter("Nim")
pp.add_printer("string", NimStringPrinter.pattern, NimStringPrinter)
pp.add_printer("array", NimArrayPrinter.pattern, NimArrayPrinter)
pp.add_printer("string", NimSeqPrinter.pattern, NimSeqPrinter)


gdb.printing.register_pretty_printer(None, pp, replace=True)

