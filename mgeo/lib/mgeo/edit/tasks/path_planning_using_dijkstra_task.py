import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

# MGeo Module
from class_defs import *

from path_planning import dijkstra

import numpy as np


class PathPlanningUsingDijkstraTask:
    def __init__(self, node_set, link_set):
        self.node_set = node_set 
        self.link_set = link_set

        self.start_node = None
        self.end_node = None  

    def set_start_node(self, node):
        self.start_node = node
    
    def get_start_node(self, node):
        return self.start_node

    def set_end_node(self, node):
        self.end_node = node

    def get_end_node(self, node):
        return self.end_node

    def clear_nodes_selected(self):
        self.start_node = None
        self.end_node = None

    def cancel(self):
        self.clear_nodes_selected()

    def do(self):
        if self.start_node is None:
            raise BaseException('Start node is not specified')

        if self.end_node is None:
            raise BaseException('End node is not specified')

        result, path = PathPlanningUsingDijkstraTask.solve_dijkstra(
            self.start_node, self.end_node, self.node_set, self.link_set)

        return result, path 


    @staticmethod
    def solve_dijkstra(start_node, end_node, node_set, link_set):
        """start_node에서 end_node로 향하는 optimal path를 찾는다 """
        dijkstra_obj = dijkstra.Dijkstra(node_set.nodes, link_set.lines)
        result, path = dijkstra_obj.find_shortest_path(start_node.idx, end_node.idx)
        if not result:
            print('[ERROR] Failed to find path Node (id={}) -> Node (id={})'.format(start_node.idx, end_node.idx))
            
        return result, path 

