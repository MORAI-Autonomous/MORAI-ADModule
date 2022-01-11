import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../'))) # mgeo가 있는 경로를 추가한다.

from class_defs import *

import numpy as np
import matplotlib.pyplot as plt


def load_test_case_001():
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


    line = Line()
    line.set_points_using_node(node_set.nodes[0], node_set.nodes[2], 1)
    line_set.append_line(line, create_new_key=True)

    line = Line()
    line.set_points_using_node(node_set.nodes[1], node_set.nodes[3], 1)
    line_set.append_line(line, create_new_key=True)

    line = Line()
    line.set_points_using_node(node_set.nodes[0], node_set.nodes[3], 1)
    line_set.append_line(line, create_new_key=True)

    line = Line()
    line.set_points_using_node(node_set.nodes[1], node_set.nodes[2], 1)
    line_set.append_line(line, create_new_key=True)

    return node_set, line_set


if __name__ == u'__main__':
    node_set, line_set = load_test_case_001()

    plt.figure()
    node_set.draw_plot(plt.gca())
    line_set.draw_plot(plt.gca())
    plt.show()