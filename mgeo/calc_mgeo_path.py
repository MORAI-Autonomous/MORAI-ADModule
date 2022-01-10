#!/usr/bin/env python3

### 
import pandas as pd

import json
import io
import os
import sys

from ..localization.point import Point
from .lib.mgeo.class_defs import *
from .e_dijkstra import Dijkstra


class mgeo_dijkstra_path :
    def __init__(self, map_name):

        current_path = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(current_path)

        load_path = os.path.normpath(os.path.join(current_path, 'lib/mgeo_data/'+map_name))
        mgeo_planner_map = MGeoPlannerMap.create_instance_from_json(load_path)

        node_set = mgeo_planner_map.node_set
        link_set = mgeo_planner_map.link_set
        self.nodes=node_set.nodes
        self.links=link_set.lines

        self.global_planner=Dijkstra(self.nodes,self.links)

    def calc_dijkstra_path(self, start_node, end_node):

        result, path = self.global_planner.find_shortest_path(start_node, end_node)
        self.x_list = []
        self.y_list = []
        self.z_list = []
        for waypoint in path["point_path"] :
            path_x = waypoint[0]
            path_y = waypoint[1]
            self.x_list.append(path_x)
            self.y_list.append(path_y)
            self.z_list.append(0.)

        path = pd.DataFrame({"x":self.x_list, "y":self.y_list, "z":self.z_list})

        path_data = path.apply(
            lambda point: Point(point["x"], point["y"]), axis=1
        ).tolist()

        return path_data