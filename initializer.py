import sys
import os
import meaningless_shoot

if 'r' in meaningless_shoot.buttons:
    args = sys.argv[:]
    args.insert(0, sys.executable)
    os.execv(sys.executable, args)
