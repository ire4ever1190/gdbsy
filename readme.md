Easy interface to debuggers in Nim. Trying to solve the issue of "please I just want to get some form of debugging"

To run, just compile with your code with `--debugger:native --import:gdbsy`. Currently only supports GDB but plan to support LLDB also (though might be a while...).
When you run GDB it will mention about autopaths, in my `~/gdbinit` file I have this, but I recommend narrowing it to the file for security reasons
```
add-auto-load-safe-path ~/.nimble/pkgs2/
add-auto-load-safe-path ~/.choosenim/toolchains
```
