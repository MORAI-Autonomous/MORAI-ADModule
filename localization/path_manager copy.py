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
            x_count = {}
            y_count = {}
            x_list_test = []
            y_list_test = []

            for window in range(-window_size, window_size):
                x = self.path[i+window].x
                y = self.path[i+window].y
                x_list_test.append(x)
                y_list_test.append(y)

            for lst_x in x_list_test:
                try: x_count[lst_x]+= 1
                except: x_count[lst_x]=1

            for lst_y in y_list_test:
                try: y_count[lst_y]+= 1
                except: y_count[lst_y]=1

            test= Point
            test.x = 0.01
            test.y = 0.01

            if len(x_list_test) == x_count[max(x_count, key=x_count.get)]:
                self.path[i].x = self.path[i].x + test.x

            if len(y_list_test) == y_count[max(y_count, key=y_count.get)]:
                self.path[i].y = self.path[i].y + test.y

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

        for i in range(len(self.path)-window_size, len(self.path) - 50):
            velocity_profile.append(max_velocity)

        for i in range(len(self.path) - 50,len(self.path)):
            velocity_profile.append(0.)

        self.velocity_profile = velocity_profile

        print("self.velocity_profile",self.velocity_profile)

    def get_local_path(self, vehicle_state):
        distance_list = [point.distance(vehicle_state.position) for point in self.path]
        current_waypoint = np.argmin(distance_list)

        if current_waypoint + self.local_path_size < len(self.path):
            local_path = self.path[current_waypoint:current_waypoint + self.local_path_size]
        else:
            local_path = self.path[current_waypoint:]
            # 연결된 경로 (closed path) 일 경우, 경로 끝과 처음을 이어준다.
            if self.is_closed_path:
                local_path += self.path[:self.local_path_size + len(self.path) - current_waypoint]

        return local_path, self.velocity_profile[current_waypoint]
