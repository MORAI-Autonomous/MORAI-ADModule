#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from .node import Node
# from .node_set import NodeSet
# from .node_set_dict import NodeSet
# from .line import Line
# from .line_set import LineSet

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

from class_defs import *
from utils import version

import numpy as np
import matplotlib.pyplot as plt


def test():

    node_set_dict = NodeSet()

    node = Node('A')
    node.point = np.array([0, 0, 0])
    node_set_dict.nodes[node.idx] = node

    node = Node('B')
    node.point = np.array([0, 0, 0])
    node_set_dict.nodes[node.idx] = node

    node = Node('C')
    node.point = np.array([0, 0, 0])
    node_set_dict.nodes[node.idx] = node


    node_set_list = utils.node_set_dict_to_list(node_set_dict)

    print('Test 1: ', node_set_list.nodes[0] is node_set_dict.nodes['A'])
    print('Test 2: ', node_set_list.nodes[1] is node_set_dict.nodes['B'])
    print('Test 3: ', node_set_list.nodes[2] is node_set_dict.nodes['C'])

    print('ENDED')

test()