import gdb
import re
from gdb.FrameDecorator import FrameDecorator

DEMANGLE_REGEX = re.compile(r"_p\d+")


class SymValueWrapper():

    def __init__(self, symbol, frame):
        self.sym = symbol.symbol()
        self.frame = frame

    def value(self):
        return self.sym.value(self.frame)

    def symbol(self):
        return DEMANGLE_REGEX.sub("", self.sym.name)


class NimFrameDecorator(FrameDecorator):
  """
  Decorates Nim frames by using the internal frame variable so that line info lines up to
  how Nim expects it.
  """

  def frame_args(self):
    """
    Demangles the arguments passed to the frame
    """
    args = super().frame_args()
    if args is None:
      return None

    # Get the arguments, remove the mangling applied to it
    return (SymValueWrapper(arg, self.inferior_frame()) for arg in args)

  def frame_locals(self):
    """
    Removes temp variables and special Nim compiler variables.
    Cleans up the local list in the debugger
    """
    gdb.write("Called")
    locals = super().frame_locals()
    if locals is None:
      return None

    # Get the arguments, remove the mangling applied to it
    gdb.write("here")
    for sym in block:
      if sym.is_argument: continue
      if sym.name.endswith("_") or "__" in sym.name: continue
      yield sym

class NimFrameFilter:
  def __init__(self):
    self.name = "nim-frame-filter"
    self.enabled = True
    self.priority = 10000
    self.hidden =  {"NimMainInner","NimMain", "main"}

  def filter(self, iterator):
    for framedecorator in iterator:
      if framedecorator.function() not in self.hidden:
        # For nim functions, we want to demangle the parameters
        if framedecorator.filename().endswith(".nim"):
          yield NimFrameDecorator(framedecorator)
        else:
          yield framedecorator

gdb.frame_filters["gdbsy-frame-filter"] = NimFrameFilter()
