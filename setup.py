import sys
from cx_Freeze import setup, Executable


build_exe_options = {"packages": ["os"], "excludes": ["tkinter"],
                     "includes": ["lxml._elementpath"]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
setup(
    name = "meets",
    version = "1.0",
    description = "Thai Box Meets",
    options = {"build_exe": build_exe_options},
    executables = [Executable("main.py", base=base)]
)
