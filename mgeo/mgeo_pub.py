#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading

import rclpy
from rclpy.node import Node

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)

from lib.mgeo.class_defs import *

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped,Point32
from sensor_msgs.msg import PointCloud

class get_mgeo :
    def __init__(self):

        rclpy.init()
        self.node = rclpy.create_node('morai_mgeo_pub')

        thread = threading.Thread(target=rclpy.spin, args=(self.node,),daemon=True)
        thread.start()

        load_path = os.path.normpath(os.path.join(current_path, 'lib/mgeo_data/V_RHT_Suburb_03'))
        mgeo_planner_map = MGeoPlannerMap.create_instance_from_json(load_path)

        node_set = mgeo_planner_map.node_set
        link_set = mgeo_planner_map.link_set
        self.nodes=node_set.nodes
        self.links=link_set.lines
        print('# of nodes: ', len(node_set.nodes))
        print('# of links: ', len(link_set.lines))

    def execute(self):
        print("start mgeo data publish")
        self._set_protocol()
        self.alllinks = self.getAllLinks()
        self.allnodes = self.getAllNode()
        while rclpy.ok():
            self._send_data(self.alllinks, self.allnodes)
        print("end mgeo data publish")

    def _set_protocol(self):
        # publisher
        self.link_pub    = self.node.create_publisher(msg_type=PointCloud,             topic="/mgeo_link",       qos_profile=10,)

        self.node_pub    = self.node.create_publisher(msg_type=PointCloud,             topic="/mgeo_node",       qos_profile=10,)

    def _send_data(self, link_data, node_data):
        self.link_pub.publish(link_data)
        self.node_pub.publish(node_data)

    def getAllLinks(self):
        all_link=PointCloud()
        all_link.header.frame_id='map'
        
        for link_idx in self.links :
            for link_point in self.links[link_idx].points:
                tmp_point=Point32()
                tmp_point.x=link_point[0]
                tmp_point.y=link_point[1]
                tmp_point.z=link_point[2]
                all_link.points.append(tmp_point)

        return all_link
    
    def getAllNode(self):
        all_node=PointCloud()
        all_node.header.frame_id='map'
        for node_idx in self.nodes :
            tmp_point=Point32()
            tmp_point.x=self.nodes[node_idx].point[0]
            tmp_point.y=self.nodes[node_idx].point[1]
            tmp_point.z=self.nodes[node_idx].point[2]
            all_node.points.append(tmp_point)

        return all_node
