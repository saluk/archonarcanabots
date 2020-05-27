import os, sys
try:
    import util
except:
    sys.path.insert(0, os.path.abspath(__file__).rsplit("/", 1)[0]+'/..')
    import util
