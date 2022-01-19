#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .point import Point
import numpy as np


class PathManager:
    def __init__(self, path, is_closed_path, local_path_size):
        self.path = path
        self.is_closed_path = is_closed_path
        self.local_path_size = local_path_size
        self.velocity_profile = []

    def set_velocity_profile(self, max_velocity, road_friction, window_size):
        # TODO: moving window를 설정하는 방식 개선.
        max_velocity = max_velocity / 3.6
        velocity_profile = []
        for i in range(0, window_size):
            velocity_profile.append(max_velocity)

        for i in range(window_size, len(self.path)-window_size):
            x_list = []
            y_list = []
            for window in range(-window_size, window_size):
                x = self.path[i+window].x
                y = self.path[i+window].y
                x_list.append([-2*x, -2*y, 1])
                y_list.append(-(x*x)-(y*y))

            x_matrix = np.array(x_list)
            y_matrix = np.array(y_list)
            x_trans = x_matrix.T

            a_matrix = np.linalg.inv(x_trans.dot(x_matrix)).dot(x_trans).dot(y_matrix)
            a = a_matrix[0]
            b = a_matrix[1]
            c = a_matrix[2]
            r = np.sqrt(a*a+b*b-c)
            target_velocity = np.clip(np.sqrt(r*9.8*road_friction), 0, max_velocity)
            velocity_profile.append(target_velocity)

        for i in range(len(self.path)-window_size, len(self.path)):
            velocity_profile.append(target_velocity)

        self.velocity_profile = velocity_profile

    def get_local_path(self, vehicle_state):
        # TODO: 최소값 구하는 로직 개선 필요.
        min_distance=float('inf')
        current_waypoint=0
        for i, point in enumerate(self.path):
            dx = point.x - vehicle_state.position.x
            dy = point.y - vehicle_state.position.y
            distance = dx*dx + dy*dy
            if distance < min_distance:
                min_distance = distance
                current_waypoint = i

        if current_waypoint + self.local_path_size < len(self.path):
            local_path = self.path[current_waypoint:current_waypoint + self.local_path_size]
        else:
            local_path = self.path[current_waypoint:]
            # 연결된 경로 (closed path) 일 경우, 경로 끝과 처음을 이어준다.
            if self.is_closed_path:
                local_path += self.path[:self.local_path_size + len(self.path) - current_waypoint]

        return local_path, self.velocity_profile[current_waypoint]
