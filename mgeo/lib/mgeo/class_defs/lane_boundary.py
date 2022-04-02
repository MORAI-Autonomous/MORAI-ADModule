#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

import numpy as np

from .line import Line

from collections import OrderedDict


class LaneBoundary(Line):
    """도로의 차선을 표현하는 선, Mesh 생성을 위해 사용된다."""
    def __init__(self, points=None, idx=None):
        super(LaneBoundary, self).__init__(points, idx)

        # Visualization 모드
        self.set_vis_mode_all_different_color(True)

        self.lane_type_def = ''
        self.lane_type = 0
        self.lane_sub_type = 0

        self.lane_color = ''
        self.lane_shape = []

        # dash solid_line_interval
        self.lane_width = 0.15 # U턴구역선이면 0.35로 변경할 것
        self.dash_interval_L1 = 30 # 도색 길이
        self.dash_interval_L2 = 50 # 빈 길이
        self.double_line_interval = 0.10 # 겹선일 때 두 선 사이의 거리, 규성상 0.10~0.15, 차선 종류와 관계없이 일정.

        # mesh를 생성하기 위한 vertices
        self.mesh_gen_vertices = [] 
        self.mesh_gen_vertex_subsets_for_each_face = [] # face를 구성할 vertices의 index를 기록한다
        self.mesh_gen_vertex_uv_coords = [] # uv 좌표
        
        # 
        self.vis_mode_marker_size = 0
        self.vis_mode_marker_style = ""

        # [210513] passRestr 추가
        self.passRestr = ''

        # [211222] rad-r 차선 shape/color 범위 추가
        self.lane_type_list = []
        self.lane_shape_list = []
        self.lane_color_list = []
        self.lane_type_start = []
        self.lane_type_end = []


    def get_lane_num(self):
        return len(self.lane_shape)


    def set_lane_type_list(self, start, end):
        self.lane_type_start.append(start)
        self.lane_type_end.append(end)


    def is_every_attribute_equal(self, another):
        """attribute가 같은지 확인한다"""
        if self.lane_type_def != another.lane_type_def:
            return False
        
        if self.lane_type != another.lane_type:
            return False

        if self.lane_sub_type != another.lane_sub_type:
            return False

        if self.lane_color != another.lane_color:
            return False

        if self.lane_shape != another.lane_shape:
            return False

        if self.lane_width != another.lane_width:
            return False

        if self.dash_interval_L1 != another.dash_interval_L1:
            return False

        if self.dash_interval_L2 != another.dash_interval_L2:
            return False

        if self.double_line_interval != another.double_line_interval:
            return False
        
        return True

  
    def get_attribute_from(self, src):
        LaneBoundary.copy_attribute(src, self)


    def to_dict(self):
        dict_data = {
            'idx': self.idx,
            'from_node_idx': self.from_node.idx if self.from_node else None,
            'to_node_idx': self.to_node.idx if self.to_node else None,
            'points': self.points.tolist(),
            'lane_type_def': self.lane_type_def,
            'lane_type': self.lane_type,
            'lane_sub_type': self.lane_sub_type,
            'lane_color': self.lane_color,
            'lane_shape': self.lane_shape,
            'lane_width': self.lane_width,
            'dash_interval_L1': self.dash_interval_L1,
            'dash_interval_L2': self.dash_interval_L2,
            'double_line_interval': self.double_line_interval,
            'geometry': self.geometry,
            'passRestr' : self.passRestr,
            'lane_type_list': self.lane_type_list,
            'lane_shape_list': self.lane_shape_list,
            'lane_color_list': self.lane_color_list,
            'lane_type_start': self.lane_type_start,
            'lane_type_end': self.lane_type_end
        }
        return dict_data


    def create_mesh_gen_points(self, solid_line_interval=0.5):
        if self.get_lane_num() == 1:
            return self.create_mesh_gen_points_single_lane(solid_line_interval)
        else:
            return self.create_mesh_gen_points_double_lane(solid_line_interval)
    
        
        # AutoEver의 road edge 타입은 일단 명확해지기 전까지 보류. 2021.11.22 정택진.
        # elif str("roadEdge") in self.idx : # RE TYPE
        #     if self.lane_sub_type == 2 :
        #         # 가드레일
        #         return make_lane_boundary.create_mesh_gen_boundary_structure_guard_rail(0)
        #     elif self.lane_sub_type == 3 :
        #         # 중앙분리대
        #         return make_lane_boundary.create_mesh_gen_boundary_structure_central_reservation(0)
        #     elif self.lane_sub_type == 4 :
        #         # 방음벽
        #         return make_lane_boundary.create_mesh_gen_boundary_structure_sound_barrier(0)
        #     elif self.lane_sub_type == 5 :
        #         # 1.5m 초과 구조물 벽
        #         return make_lane_boundary.create_mesh_gen_boundary_structure_sound_barrier(0)
        #     elif self.lane_sub_type == 12 :
        #         # 0.3m 초과 1.5m 이하 구조물 배리어.
        #         return make_lane_boundary.create_mesh_gen_boundary_structure_guard_rail(1)


    def create_mesh_gen_points_single_lane(self, solid_line_interval=0.5):
        """일정 간격으로 mesh gen point를 생성한다. 이 때, 본 클래스의 point는 0.1m 간격으로 채워져있어야한다.
        mesh gen point란, points를 기준으로, mesh를 생성할 수 있는 point를 차선을 기준으로 위 아래에 생성하는 것이다.
      

        [single lane이면]

        (0) <-- 0.5m --> (2) <-- 0.5m --> (4)
        --------------------------------------
        (1)              (3)              (5) 
        """
        self.mesh_gen_vertices = []
        self.mesh_gen_vertex_subsets_for_each_face = []
        self.mesh_gen_vertex_uv_coords = [] # uv 좌표

        # 
        point_step = 0.1

        # 실선일 때
        solid_only_step = int(solid_line_interval/point_step)

        below_exec = False

        if 'Broken' in self.lane_shape:
            # 점선일 때는 다음의 계산이 필요 
            dash_interval_L1 = self.dash_interval_L1
            dash_interval_L2 = self.dash_interval_L2
            L1L2 = dash_interval_L1 + dash_interval_L2
            if L1L2 == 0.0:
                return self.mesh_gen_vertices, self.mesh_gen_vertex_subsets_for_each_face, self.mesh_gen_vertex_uv_coords

            # 남는 길이를 계산하고, 이를 다시 적당히 분배해야 한다
            total_length = len(self.points) * point_step
            total_num_set = int(np.floor(total_length / L1L2))
            if total_num_set == 0: # delta 계산을 위해 total_num_set으로 나눠야하므로 계산 필요
                return self.mesh_gen_vertices, self.mesh_gen_vertex_subsets_for_each_face, self.mesh_gen_vertex_uv_coords
            remainder = total_length % L1L2
            delta = remainder / (total_num_set * 2)
            
            
            # 이만큼을 각 점선 길이에 더해주면 된다
            dash_interval_L1 += delta
            dash_interval_L2 += delta

            # 이를 point index 단위로 바꾸면 아래와 같다 (ceil, floor를 일부러 교차함)
            dashed_step_L1 = int(np.ceil(dash_interval_L1/point_step))
            dashed_step_L2 = int(np.floor(dash_interval_L2/point_step))

            below_exec = True


        i = 0
        face_cnt = 0
        paint = True # 점선일 때, 그리는 구간 / 넘어가는 구간을 토글링하기 위한 변수
        uv_idx = 0 # uv 좌표 카운팅.
        once_flag = True
        # t = 0
        
        if self.lane_shape[0] == 'Solid':
            # 남은 포인트의 개수.
            remain_points = len(self.points) % solid_only_step
            # 남은 포인트와 원래 간격의 비율.
            remain_ratio = remain_points / solid_only_step

        slice_count = -1
        while i < len(self.points):
            """STEP #01 vertex 생성을 위해 현재 lane marking에서 수직한 벡터 계산"""
            # 현재 위치에서의 벡터 계산
            if i == len(self.points) - 1:                   # 마지막 값이면, 이전 값과의 차이로 계산
                vect = self.points[i] - self.points[i-1]
            elif i != 0 and i < len(self.points) - 1:       # 중간 각을 위해 앞, 뒤 벡터 를 이용하여 계산.
                vect = self.points[i+1] - self.points[i-1]
            else:                                           # index = 0
                vect = self.points[i+1] - self.points[i]
            vect = vect / np.linalg.norm(vect, ord=2)
            
            # 현재 벡터를 xy평면상에서 +-90deg 회전시킨다.
            pos_vect_ccw = self.rorate_around_z_axis(np.pi/2, vect)
            pos_vect_cw = self.rorate_around_z_axis(-np.pi/2, vect)
            
            # 여기서 z값은 그냥 0으로 한다
            pos_vect_ccw[2] = 0
            pos_vect_cw[2] = 0


            """STEP #02 Mesh 생성을 위한 vertex 생성하기"""
            # 위 아래로 width/2 위/아래로 움직이면 된다.
            lane_width_ratio = 1.0
            if self.check_inflection_point(False, solid_only_step, i):      # 곡선 구간 up, dn 버텍스 간격의 길이 보간
                lane_width_ratio = 1.414 # 루트2
                if i != 0 and i != len(self.points) - 1:
                    before_vec = self.points[i - 1] - self.points[i]
                    after_vec = self.points[i + 1] - self.points[i]
                    dot_value = self.calc_dot_product(before_vec, after_vec)
                    bet_radian = np.emath.arccos(dot_value)
                    bet_degree = bet_radian * 180 / np.math.pi
                    sin_value = np.sin(bet_radian)
                    # 예각이 심해지면 뾰족해서 어색하기에 weight 를 더 해줌
                    if bet_degree < 50: sin_value = sin_value ** 2
                    lane_width_ratio = lane_width_ratio * sin_value

            pos_vect_ccw = pos_vect_ccw * self.lane_width * lane_width_ratio / 2.0
            pos_vect_cw = pos_vect_cw * self.lane_width * lane_width_ratio / 2.0

            # 이를 현재 위치에서 더해주면 된다. 이 때 numpy array가 아닌 일반 list로 저장한다 (vtk에서 numpy array 지원X)
            up = (self.points[i] + pos_vect_ccw).tolist()
            dn = (self.points[i] + pos_vect_cw).tolist()

            self.mesh_gen_vertices.append(up)
            self.mesh_gen_vertices.append(dn)

            if self.lane_shape[0] == 'Solid':
                """ Case #A 단선, 실선인 경우"""
                i += solid_only_step
                if i >= len(self.points) and once_flag:
                    i = len(self.points) - 1
                    once_flag = False
            else:
                """ Case #B 단선, 점선인 경우"""
                if paint:
                    # 이번에 페인트 칠을 하는거라면, 페인트 칠해야하는 구간인 L1만큼 앞으로 나간다
                    i += dashed_step_L1
                    # i += 1
                    # t += 1
                    # if t > dashed_step_L1:
                    #     paint = False
                    #     t = 0
                else: 
                    # 페인트 칠을 하지 않고 건너뛰는 거면, L2만큼 앞으로 나간다
                    i += dashed_step_L2
                    # i += 1
                    # t += 1
                    # if t > dashed_step_L2:
                    #     paint = True
                    #     t = 0

            """STEP #03 위에서 생성한 vertex로 face를 만들기 위한 vertex 조합을 생성한다"""
            if face_cnt > 0: # 첫번째 loop에는 하지 않기 위함
                if self.lane_shape[0] == 'Solid' or paint:
                    # face_cnt = 1 일 때, [0, 1, 3, 2]
                    # face_cnt = 2 일 때, [2, 3, 5, 4]
                    start_id = (face_cnt - 1) * 2
                    face = [start_id, start_id+1, start_id+3, start_id+2]

                    self.mesh_gen_vertex_subsets_for_each_face.append(face)

            """UV index 지정한다."""
            # uv 인덱스의 간격은 fix되면 프로젝트에서 계속 유지되어야 하므로, 협의하여 정합니다.
            self.mesh_gen_vertex_uv_coords.append([uv_idx, 0])
            self.mesh_gen_vertex_uv_coords.append([uv_idx, 1])
            if self.lane_shape[0] == 'Solid':
                # 실선의 경우, 계속 증가하도록.
                if i == len(self.points) - 1:
                    uv_idx += (1 - remain_ratio)
                else:
                    if slice_count >= 0:
                        uv_idx += 1 / 5
                    else:
                        uv_idx += 1
            else:
                # 점선의 경우 같은 uv coord가 반복 되도록 ex) (0, 0) (6, 1) ------ (0, 0) (6, 1) ---... 
                if paint:
                    uv_idx = 0
                else:
                    uv_idx = 6

            face_cnt += 1 # face_cnt는 실제 paint를 칠한 것 여부와 관계없이 증가
            paint = not paint # paint 칠했으면 다음번엔 칠하지 않아야하므로 토글

            """ 다음 노드와 이전 노드의 각이 급격하게 꺾이면 메쉬가 이상해지므로 보간해줍니다. """
            if self.check_inflection_point(True, solid_only_step, i):
                solid_only_step = int(solid_line_interval/0.5)
                slice_count = int(solid_line_interval/point_step) + 10 # 크게 잡아서 더 부드럽게 보이도록 하였습니다.
            else:
                slice_count -= 1
                if slice_count < 0:
                    solid_only_step = int(solid_line_interval/point_step)

        return self.mesh_gen_vertices, self.mesh_gen_vertex_subsets_for_each_face, self.mesh_gen_vertex_uv_coords
        

    def create_mesh_gen_points_double_lane(self, solid_line_interval=0.5):
        """일정 간격으로 mesh gen point를 생성한다. 이 때, 본 클래스의 point는 0.1m 간격으로 채워져있어야한다.
        mesh gen point란, points를 기준으로, mesh를 생성할 수 있는 point를 차선을 기준으로 위 아래에 생성하는 것이다.
  
        [double lane이면]

        (0) <-- 0.5m --> (4) <-- 0.5m --> (8)

        (1) <-- 0.5m --> (5) <-- 0.5m --> (9)
        --------------------------------------
        (2)              (6)              (10)   

        (3)              (7)              (11)   
        """
        self.mesh_gen_vertices = []
        self.mesh_gen_vertex_subsets_for_each_face = []
        self.mesh_gen_vertex_uv_coords = [] # uv 좌표
        # 
        point_step = 0.1

        # 실선일 때
        solid_only_step = int(solid_line_interval/point_step)

        below_exec = False

        if 'Broken' in self.lane_shape:
            # 점선일 때는 다음의 계산이 필요
            dash_interval_L1 = self.dash_interval_L1
            dash_interval_L2 = self.dash_interval_L2
            L1L2 = dash_interval_L1 + dash_interval_L2
            if L1L2 == 0.0:
                return self.mesh_gen_vertices, self.mesh_gen_vertex_subsets_for_each_face, self.mesh_gen_vertex_uv_coords

            # 남는 길이를 계산하고, 이를 다시 적당히 분배해야 한다 (dashed line일 때만 계산한다)
            total_length = len(self.points) * point_step
            total_num_set = int(np.floor(total_length / L1L2))
            if total_num_set == 0: # delta 계산을 위해 total_num_set으로 나눠야하므로 계산 필요
                return self.mesh_gen_vertices, self.mesh_gen_vertex_subsets_for_each_face, self.mesh_gen_vertex_uv_coords
            remainder = total_length % L1L2
            delta = remainder / (total_num_set * 2)
            

            # 이만큼을 각 점선 길이에 더해주면 된다
            dash_interval_L1 += delta
            dash_interval_L2 += delta

            # 이를 point index 단위로 바꾸면 아래와 같다 (ceil, floor를 일부러 교차함)
            dashed_step_L1 = int(np.ceil(dash_interval_L1/point_step))
            dashed_step_L2 = int(np.floor(dash_interval_L2/point_step))

            below_exec = True


        i = 0
        face_cnt = 0
        paint = True # 점선일 때, 그리는 구간 / 넘어가는 구간을 토글링하기 위한 변수
        uv_idx = 0 # uv 좌표 카운팅.

        while i < len(self.points):

            """STEP #01 vertex 생성을 위해 현재 lane marking에서 수직한 벡터 계산"""
            # 현재 위치에서의 벡터 계산
            if i == len(self.points) - 1: # 마지막 값이면, 이전 값과의 차이로 계산
                vect = self.points[i] - self.points[i-1]
            else:
                vect = self.points[i+1] - self.points[i]
            vect = vect / np.linalg.norm(vect, ord=2)

            # 현재 벡터를 xy평면상에서 +-90deg 회전시킨다.
            pos_vect_ccw = self.rorate_around_z_axis(np.pi/2, vect)
            pos_vect_cw = self.rorate_around_z_axis(-np.pi/2, vect)
            
            # 여기서 z값은 그냥 0으로 한다
            pos_vect_ccw[2] = 0
            pos_vect_cw[2] = 0


            """STEP #02 Mesh 생성을 위한 vertex 생성하기"""
            # 위 아래로 width/2 위/아래로 움직이면 된다.
            pos_vect_ccw1 = pos_vect_ccw * (self.double_line_interval / 2.0 + self.lane_width)
            pos_vect_ccw2 = pos_vect_ccw * (self.double_line_interval / 2.0)
            pos_vect_cw1 = pos_vect_cw * (self.double_line_interval / 2.0)
            pos_vect_cw2 = pos_vect_cw * (self.double_line_interval / 2.0 + self.lane_width)

            # 이를 현재 위치에서 더해주면 된다. 이 때 numpy array가 아닌 일반 list로 저장한다 (vtk에서 numpy array 지원X)
            up1 = (self.points[i] + pos_vect_ccw1).tolist()
            up2 = (self.points[i] + pos_vect_ccw2).tolist()
            dn1 = (self.points[i] + pos_vect_cw1).tolist()
            dn2 = (self.points[i] + pos_vect_cw2).tolist()

            self.mesh_gen_vertices.append(up1)
            self.mesh_gen_vertices.append(up2)
            self.mesh_gen_vertices.append(dn1)
            self.mesh_gen_vertices.append(dn2)

            self.mesh_gen_vertex_uv_coords.append([uv_idx, 0])
            self.mesh_gen_vertex_uv_coords.append([uv_idx, 1]) 
            self.mesh_gen_vertex_uv_coords.append([uv_idx, 0])
            self.mesh_gen_vertex_uv_coords.append([uv_idx, 1])

            if 'Broken' in self.lane_shape and 'Solid' in self.lane_shape:
                # 점선과 실선이 합쳐진 경우.
                uv_idx += 6
            else:
                uv_idx += 1

            if 'Broken' not in self.lane_shape:
                """ 모두 실선인 경우"""
                i += solid_only_step
            else:
                """ 점선이 섞여있는 경우"""
                if paint:
                    # 이번에 페인트 칠을 하는거라면, 페인트 칠해야하는 구간인 L1만큼 앞으로 나간다
                    i += dashed_step_L1
                else: 
                    # 페인트 칠을 하지 않고 건너뛰는 거면, L2만큼 앞으로 나간다
                    i += dashed_step_L2

            """STEP #03 위에서 생성한 vertex로 face를 만들기 위한 vertex 조합을 생성한다"""
            if face_cnt > 0: # 첫번째 loop에는 하지 않기 위함

                # face_cnt = 1 일 때, [0, 1, 5, 4], [2, 3, 7, 6]
                # face_cnt = 2 일 때, [4, 5, 9, 8], [6, 7, 11, 10]

                start_id = (face_cnt - 1) * 4
                face1 = [start_id+0, start_id+1, start_id+5, start_id+4]
                face2 = [start_id+2, start_id+3, start_id+7, start_id+6]

                if self.lane_shape[0] == 'Solid' or paint: # solid 일 때는 항상 paint = True이므로, lane_shape는 신경쓰지 않아도 된다.
                    self.mesh_gen_vertex_subsets_for_each_face.append(face1)

                if self.lane_shape[1] == 'Solid' or paint:
                    self.mesh_gen_vertex_subsets_for_each_face.append(face2)

            face_cnt += 1 # face_cnt는 실제 paint를 칠한 것 여부와 관계없이 증가
            paint = not paint # paint 칠했으면 다음번엔 칠하지 않아야하므로 토글  
            
        return self.mesh_gen_vertices, self.mesh_gen_vertex_subsets_for_each_face, self.mesh_gen_vertex_uv_coords
            
            
    def rorate_around_z_axis(self, angle, point):
        rotation = np.array([
            [np.cos(angle), -np.sin(angle), 0.0],
            [np.sin(angle),  np.cos(angle), 0.0],
            [0.0, 0.0, 1.0]])

        transform_pt = rotation.dot(point)
        return transform_pt

    def rotate_around_vector_axis(self, angle, axis, point) :
        mat = self.rotation_matrix(axis, angle)

        transform_pt = mat.dot(point)
        return transform_pt

    def rotation_matrix(self, axis, theta):
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.
        """
        
        axis = np.asarray(axis)
        axis = axis / np.math.sqrt(np.dot(axis, axis))
        a = np.cos(theta / 2.0)
        b, c, d = -axis * np.sin(theta / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                        [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                        [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])
    
    def draw_plot(self, axes):
        # if self.get_lane_num() != 2:
        #     return
        # if self.lane_type != 502:
        #     return
            
        # 그려야하는 width와 color가 지정되어 있으면 해당 값으로만 그린다
        if self.vis_mode_line_width is not None and \
            self.vis_mode_line_color is not None:
            self.plotted_obj = axes.plot(self.points[:,0], self.points[:,1],
                linewidth=self.vis_mode_line_width,
                color=self.vis_mode_line_color,
                markersize=self.vis_mode_marker_size,
                marker=self.vis_mode_marker_style)
            return
        

        if self.get_vis_mode_all_different_color():
            # 모두 다르게 그리라고하면, 색을 명시하지 않으면 된다
            self.plotted_obj = axes.plot(self.points[:,0], self.points[:,1],
                markersize=self.vis_mode_marker_size,
                marker=self.vis_mode_marker_style)
        
        else:
            # 이 경우에는 선의 종류에 따라 정해진 색과 모양으로 그린다
            
            if not self.included_plane:
                # 이는 list of matplotlib.lines.Line2D 인스턴스를 반환
                self.plotted_obj = axes.plot(self.points[:,0], self.points[:,1],
                    markersize=self.vis_mode_marker_size,
                    marker=self.vis_mode_marker_style,
                    color='k')
            else:
                self.plotted_obj = axes.plot(self.points[:,0], self.points[:,1],
                    markersize=self.vis_mode_marker_size,
                    marker=self.vis_mode_marker_style,
                    color='b')

        


    @staticmethod
    def from_dict(dict_data, node_set=None):
        idx = dict_data['idx']
        from_node_idx = dict_data['from_node_idx']
        to_node_idx = dict_data['to_node_idx']
        points = np.array(dict_data['points'])
        start_node = None
        end_node = None
        
        """이제 node와 연결해준다"""
        if node_set is not None:
            if from_node_idx in node_set.nodes :
                start_node = node_set.nodes[from_node_idx]
            if to_node_idx in node_set.nodes :
                end_node = node_set.nodes[to_node_idx]

        lane_boundary = LaneBoundary(points=points, idx=idx)
        if start_node != None :
            lane_boundary.set_from_node(start_node)
        if end_node != None :
            lane_boundary.set_to_node(end_node)

        if 'lane_type_def' in dict_data:
            lane_boundary.lane_type_def = dict_data['lane_type_def']
        elif 'lane_code_def' in dict_data:
            lane_boundary.lane_type_def = dict_data['lane_code_def']
        
        if 'lane_type' in dict_data:
            lane_boundary.lane_type = dict_data['lane_type']
        elif 'lane_code' in dict_data:
            lane_boundary.lane_type = dict_data['lane_code']

        if 'lane_sub_type' in dict_data:
            lane_boundary.lane_sub_type = dict_data['lane_sub_type']

        lane_boundary.lane_color = dict_data['lane_color']
        lane_boundary.lane_shape = dict_data['lane_shape']
        lane_boundary.lane_width = dict_data['lane_width']
        lane_boundary.dash_interval_L1 = dict_data['dash_interval_L1']
        lane_boundary.dash_interval_L2 = dict_data['dash_interval_L2']
        lane_boundary.double_line_interval = dict_data['double_line_interval']
        if 'geometry' in dict_data:
            lane_boundary.geometry = dict_data['geometry']
        if 'passRestr' in dict_data:
            lane_boundary.passRestr = dict_data['passRestr']
        if 'lane_type_list' in dict_data:
            lane_boundary.lane_type_list = dict_data['lane_type_list']
        if 'lane_shape_list' in dict_data:
            lane_boundary.lane_shape_list = dict_data['lane_shape_list']
        if 'lane_color_list' in dict_data:
            lane_boundary.lane_color_list = dict_data['lane_color_list']
        if 'lane_type_start' in dict_data:
            lane_boundary.lane_type_start = dict_data['lane_type_start']
        if 'lane_type_end' in dict_data:
            lane_boundary.lane_type_end = dict_data['lane_type_end']
        

        return lane_boundary

    
    @staticmethod
    def copy_attribute(src, dst):
        dst.lane_type_def = src.lane_type_def
        dst.lane_type = src.lane_type
        dst.lane_sub_type = src.lane_sub_type

        dst.lane_color = src.lane_color
        dst.lane_shape = src.lane_shape

        # dash solid_line_interval
        dst.lane_width = src.lane_width
        dst.dash_interval_L1 = src.dash_interval_L1
        dst.dash_interval_L2 = src.dash_interval_L2
        dst.double_line_interval = src.double_line_interval

        dst.passRestr = src.passRestr


    def item_prop(self):
        item = self.to_dict()
        prop_data = OrderedDict()

        prop_data['idx'] = {'type' : 'string', 'value' : item['idx']}
        prop_data['points'] = {'type' : 'list<list<float>>', 'value' : item['points']}
        prop_data['from_node_idx'] = {'type' : 'string', 'value' : item['from_node_idx']}
        prop_data['to_node_idx'] = {'type' : 'string', 'value' : item['to_node_idx']}
        prop_data['lane_type'] = {'type' : 'int', 'value' : item['lane_type']}
        prop_data['lane_sub_type'] = {'type' : 'int', 'value' : item['lane_sub_type']}
        prop_data['lane_type_def'] = {'type' : 'string', 'value' : item['lane_type_def']}
        prop_data['lane_color'] = {'type' : 'string', 'value' : item['lane_color']}
        prop_data['lane_shape'] = {'type' : 'string', 'value' : item['lane_shape']}
        prop_data['lane_width'] = {'type' : 'float', 'value' : item['lane_width']}
        prop_data['dash_interval_L1'] = {'type' : 'float', 'value' : item['dash_interval_L1']}
        prop_data['dash_interval_L2'] = {'type' : 'float', 'value' : item['dash_interval_L2']}
        prop_data['double_line_interval'] = {'type' : 'float', 'value' : item['double_line_interval']}
        prop_data['geometry'] = {'type' : 'list<dict>', 'value' : item['geometry']}
        prop_data['passRestr'] = {'type' : 'string', 'value' : item['passRestr']}
        prop_data['lane_type_list'] = {'type' : 'list<int>', 'value' : item['lane_type_list']}
        prop_data['lane_shape_list'] = {'type' : 'list<string>', 'value' : item['lane_shape_list']}
        prop_data['lane_color_list'] = {'type' : 'list<string>', 'value' : item['lane_color_list']}
        prop_data['lane_type_start'] = {'type' : 'list<float>', 'value' : item['lane_type_start']}
        prop_data['lane_type_end'] = {'type' : 'list<float>', 'value' : item['lane_type_end']}

        return prop_data

    def get_last_idx(self):
        return self.points.shape[0] - 1

    def calc_dot_product(self, vec_1, vec_2):
        vect_1_norm = vec_1 / np.linalg.norm(vec_1, ord=2)
        vect_2_norm = vec_2 / np.linalg.norm(vec_2, ord=2)
        dot_value = np.dot(vect_1_norm, vect_2_norm)
        if dot_value > 1.0 : dot_value = 1.0
        elif dot_value < -1.0 : dot_value = -1.0

        return dot_value

    # 자신의 방향벡터와 다음 포인트의 방향벡터와의 각을 계산합니다.
    def get_gradient_first_node(self, point_idx, solid_step):
        if point_idx == len(self.points) - 1:
            return -1 # 마지막이면 평행하다고 판단.
        elif point_idx + solid_step >= len(self.points) - 1:
            return -1 # 인덱스를 넘어가면 평행하다고 판단.
        elif point_idx + (solid_step * 2) >= len(self.points) - 1:
            return -1 # 인덱스를 넘어가면 평행하다고 판단.
        else:
            vect_1 = self.points[point_idx] - self.points[point_idx + solid_step]
            vect_2 = self.points[point_idx + (solid_step * 2)] - self.points[point_idx + solid_step]
            dot_value = self.calc_dot_product(vect_1, vect_2)
            return dot_value

    def get_gradient_center_node(self, point_idx, solid_step):
        if point_idx == len(self.points) - 1:
            return -1 # 마지막이면 평행하다고 판단.
        elif point_idx + solid_step >= len(self.points) - 1:
            return -1 # 인덱스를 넘어가면 평행하다고 판단.
        if point_idx - solid_step < 0:
            return -1
        else:
            vect_1 = self.points[point_idx - solid_step] - self.points[point_idx]
            vect_2 = self.points[point_idx + solid_step] - self.points[point_idx]
            dot_value = self.calc_dot_product(vect_1, vect_2)
            return dot_value
        
    def check_inflection_point(self, is_first_node, cur_solid_only_step, cur_idx):
        if self.lane_shape[0] == 'Solid' and (cur_idx < len(self.points) - 1) and (cur_idx > 0):
            dot_value = 0
            if is_first_node:
                dot_value = self.get_gradient_first_node(cur_idx, cur_solid_only_step)    # 각 구함 (라디안)
            else:
                dot_value = self.get_gradient_center_node(cur_idx, cur_solid_only_step)
            # 0 이면 수직, +-0.5
            next_radian = np.emath.arccos(dot_value)                                      # 보기 편하게 디그리 변환.
            next_degree = next_radian * 180 / np.math.pi
            threshold_degree = 150                                                          # 급격한 각의 기준.

            # if self.idx == 'B219AS318667':
            #     Logger.log_debug('lane idx: {} dot: {}, radian: {}, degree: {}'.format(cur_idx, dot_value, next_radian, next_degree))
            
            if ((next_degree < threshold_degree) or (next_degree > 360 - threshold_degree)):
                return True
        
        return False