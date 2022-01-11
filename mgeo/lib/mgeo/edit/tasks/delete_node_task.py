import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

# MGeo Module
from class_defs import *
from edit.funcs import edit_node

import numpy as np


class DeleteNodeTask:
    def __init__(self, node_set):
        self.node_set = node_set


    def do(self, nodes):
        """node_set에서 node를 제거한다

        Parameters
        ----------
        nodes
            삭제할 node 또는 node list
        """
        if isinstance(nodes, list):
            for node in nodes:
                edit_node.delete_node(self.node_set, node)
        else:
            edit_node.delete_node(self.node_set, node)


