#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from ..localization.point import Point


class ForwardObjectDetector(object):
    def __init__(self, static_object_list=[]):
        """전방 장애물 유무 확인 (static_object_list: 정지선 신호 / dynamic_object_list: 차량, 사람)"""
        self._static_object_list = static_object_list
        self._dynamic_object_list = []

    @property
    def dynamic_object_list(self):
        return self._dynamic_object_list

    @dynamic_object_list.setter
    def dynamic_object_list(self, dynamic_object_list):
        self._dynamic_object_list = dynamic_object_list

    def detect_object(self, vehicle_state):
        tmp_translation = vehicle_state.position
        tmp_t = np.array([[np.cos(vehicle_state.yaw), -np.sin(vehicle_state.yaw), tmp_translation.x],
                          [np.sin(vehicle_state.yaw), np.cos(vehicle_state.yaw), tmp_translation.y],
                          [0, 0, 1]])
        tmp_det_t = np.array([[tmp_t[0][0], tmp_t[1][0], -(tmp_t[0][0]*tmp_translation.x+tmp_t[1][0]*tmp_translation.y)],
                              [tmp_t[0][1], tmp_t[1][1], -(tmp_t[0][1]*tmp_translation.x+tmp_t[1][1]*tmp_translation.y)],
                              [0, 0, 1]])

        object_info_dic_list = []
        for object_info in self._dynamic_object_list + self._static_object_list:
            global_position_vector = np.array([[object_info.position.x], [object_info.position.y], [1]])
            local_position_vector = tmp_det_t.dot(global_position_vector)
            local_position = Point(local_position_vector[0][0], local_position_vector[1][0])
            if local_position.x > 0:
                object_info_dic_list.append({"object_info": object_info, "local_position": local_position})

        return object_info_dic_list
