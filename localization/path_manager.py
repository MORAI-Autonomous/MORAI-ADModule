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

            x_start  = x_list[0]
            x_end    = x_list[-1]
            x_mid    = x_list[int(len(x_list)/2)]

            y_start  = y_list[0]
            y_end    = y_list[-1]
            y_mid    = y_list[int(len(y_list)/2)]

            dSt = np.array([x_start - x_mid, y_start - y_mid])
            dEd = np.array([x_end - x_mid, y_end - y_mid])

            Dcom = 2 * (dSt[0]*dEd[1] - dSt[1]*dEd[0])

            dSt2 = np.dot(dSt,dSt)
            dEd2 = np.dot(dEd,dEd)

            U1 = (dEd[1] * dSt2 - dSt[1] * dEd2)/Dcom
            U2 = (dSt[0] * dEd2 - dEd[0] * dSt2)/Dcom

            tmp_r = sqrt(pow(U1, 2)+ pow(U2, 2))

            if np.isnan(tmp_r):
                tmp_r = float('inf')

            target_velocity = sqrt(tmp_r*9.8*road_friction)

            if target_velocity > max_velocity:
                target_velocity = max_velocity

            velocity_profile.append(target_velocity)

        for i in range(len(self.path)-window_size, len(self.path) - 10):
            velocity_profile.append(max_velocity)

        for i in range(len(self.path) - 10,len(self.path)):
            velocity_profile.append(0.)

        self.velocity_profile = velocity_profile

        print('velocity_profile',velocity_profile)

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