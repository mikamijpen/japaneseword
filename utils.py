import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # PyInstaller-created exe
        base_path = os.path.dirname(sys.executable)
    else:
        # A normal .py script
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path) 