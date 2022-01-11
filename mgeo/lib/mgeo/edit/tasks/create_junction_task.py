import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

# MGeo Module
from class_defs import *


class CreateJunctionTask:
    def __init__(self, junction_set):
        self.nodes = list()
        self.junction_set = junction_set
    
    def clear_nodes_selected(self):
        self.nodes = list()

    def add_nodes(self, node):
        self.nodes.append(node)

    def create_junction(self):
        pass

    def mode_enter(self):
        pass 

    def do(self):
        pass

    def cancel(self):
        pass

    def confirm(self):
        pass


