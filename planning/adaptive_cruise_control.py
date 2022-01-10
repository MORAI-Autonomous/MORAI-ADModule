#!/usr/bin/env python
# -*- coding: utf-8 -*-
class AdaptiveCruiseControl:
    def __init__(self, velocity_gain, distance_gain, time_gap, vehicle_length):
        self.velocity_gain = velocity_gain
        self.distance_gain = distance_gain
        self.time_gap = time_gap
        self.vehicle_length = vehicle_length

        self.object_type = None
        self.object_distance = 0
        self.object_velocity = 0

    def check_object(self, local_path, object_info_dic_list, current_traffic_light):
        """경로상의 장애물 유무 확인 (차량, 사람, 정지선 신호)"""
        self.object_type = None
        min_relative_distance = float('inf')
        for object_info_dic in object_info_dic_list:
            object_info = object_info_dic['object_info']
            local_position = object_info_dic['local_position']

            object_type = object_info.type
            if object_type == 0:
                distance_threshold = 4.35
            elif object_type in [1, 2]:
                distance_threshold = 2.5
            elif object_type == 3:
                if current_traffic_light and object_info.name == current_traffic_light[0] and not current_traffic_light[1] in [16, 48]:
                    distance_threshold = 9
                else:
                    continue
            else:
                continue

            for point in local_path:
                distance_from_path = point.distance(object_info.position)

                if distance_from_path < distance_threshold:
                    relative_distance = local_position.distance()
                    if relative_distance < min_relative_distance:
                        min_relative_distance = relative_distance
                        self.object_type = object_type
                        self.object_distance = relative_distance - self.vehicle_length
                        self.object_velocity = object_info.velocity

    def get_target_velocity(self, ego_vel, target_vel):
        out_vel = target_vel

        if self.object_type == 0:
            print("ACC ON_Person")
            default_space = 8
        elif self.object_type in [1, 2]:
            print("ACC ON_Vehicle")
            default_space = 5
        elif self.object_type == 3:
            print("ACC ON_Traffic Light")
            default_space = 3
        else:
            # print("CC ON")
            return out_vel

        velocity_error = ego_vel - self.object_velocity

        safe_distance = ego_vel*self.time_gap+default_space
        distance_error = safe_distance - self.object_distance

        acceleration = -(self.velocity_gain*velocity_error + self.distance_gain*distance_error)
        out_vel = min(ego_vel+acceleration, target_vel)

        if self.object_type == 0 and (distance_error > 0):
            out_vel = out_vel - 5.

        if self.object_distance < default_space:
            out_vel = 0.

        return out_vel
