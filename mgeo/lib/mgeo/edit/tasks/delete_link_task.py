import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

# MGeo Module
from class_defs import *
from edit.funcs import edit_link

import numpy as np


class DeleteLinkTask:
    def __init__(self, link_set):
        self.link_set = link_set


    def do(self, links):
        if isinstance(links, list):
            for link in links:
                edit_link.delete_link(self.link_set, link)    
        else:
            edit_link.delete_link(self.link_set, links)


   


