#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

from class_defs import LineSet, NodeSet, Node, Link

import numpy as np
import matplotlib.pyplot as plt

line_set = LineSet() 
node_set = NodeSet()

node = Node(0)
node.point = np.array([0, 0, 0])
node_set.append_node(node) 

node = Node(1)
node.point = np.array([5, 0, 0])
node_set.append_node(node) 

node = Node(2)
node.point = np.array([0, 35, 0])
node_set.append_node(node) 

node = Node(3)
node.point = np.array([5, 35, 0])
node_set.append_node(node) 



line = Link(lazy_point_init=True)
line.set_points_using_node_lazy_init(node_set.nodes[0], node_set.nodes[3])
line_set.append_line(line, create_new_key=True)

line = Link(lazy_point_init=True)
line.set_points_using_node_lazy_init(node_set.nodes[1], node_set.nodes[2])
line_set.append_line(line, create_new_key=True)


plt.figure()
node_set.draw_plot(plt.gca())
line_set.draw_plot(plt.gca())
plt.show()