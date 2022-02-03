import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

# MGeo Module
from class_defs import *
from edit.funcs import edit_link
import numpy as np


class DeleteLineTask:
    def __init__(self, line_set):
        self.line_set = line_set


    def do(self, lines):
        if isinstance(links, list):
            for line in lines:
                edit_line.delete_line(self.line_set, line)   
        else:
            edit_line.delete_line(self.line_set, lines)



