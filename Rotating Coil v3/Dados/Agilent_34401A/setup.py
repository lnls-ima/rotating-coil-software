import sys
from cx_Freeze import setup, Executable

includes = ["sip","re","atexit","PyQt4.QtCore","matplotlib.backends.backend_tkagg"]
exe = Executable(script="Campo_34401A.py", base="Win32GUI")
 
setup(options = {"build_exe": {"includes":includes}}, executables = [exe])
