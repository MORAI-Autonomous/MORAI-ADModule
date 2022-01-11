#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .point import Point
import numpy as np
from math import sqrt,pi 


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

        target_velocity = max_velocity

        for i in range(window_size, len(self.path)-window_size):
            x_list = []
            y_list = []
            for window in range(-window_size, window_size):
                x = self.path[i+window].x
                y = self.path[i+window].y
                x_list.append(x)
                y_list.append(y)

            fp = np.polyfit(x_list, y_list, 2)
            a = fp[0]
            b = fp[1]
            c = fp[2]

            f   = abs(a*self.path[i].x+b*self.path[i].x +c)
            f_  = abs(2*a*self.path[i].x+b)
            f__ = abs(2*a)

            # numerator = pow((1 + f_),3/2)
            numerator = (1 + pow(f_,2))*sqrt(1+pow(f_,2))
            denominator = f__

            r = (numerator/denominator)


            target_velocity = sqrt(r*9.8*road_friction)

            if target_velocity > max_velocity:
                target_velocity = max_velocity

            velocity_profile.append(target_velocity)

        for i in range(len(self.path)-window_size, len(self.path) - 10):
            velocity_profile.append(max_velocity)

        for i in range(len(self.path) - 10,len(self.path)):
            velocity_profile.append(0.)

        self.velocity_profile = velocity_profile

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