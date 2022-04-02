#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

import numpy as np 
from class_defs.surface_marking import SurfaceMarking
from collections import OrderedDict


class SingleCrosswalk(SurfaceMarking):
    def __init__(self, points=None, idx=None, cw_type=None):
        super(SingleCrosswalk, self).__init__(points, idx)

        self.orign_points = [] # 원본 points
        self.points = points
        self.sign_type = cw_type
        self.ref_crosswalk_id = ''
        self.link_id_list = []
    
    def remove_ref_crosswalk_id(self, id):
        if self.ref_crosswalk_id == id:
            self.ref_crosswalk_id = ''

    def set_points(self, points):
        super(SingleCrosswalk, self).set_points(points)
    
    def item_prop(self):
        prop_data = OrderedDict()
        prop_data['idx'] = {'type' : 'string', 'value' : self.idx }
        prop_data['points'] = {'type' : 'list<list<float>>', 'value' : self.points.tolist() if type(self.points) != list else self.points }
        prop_data['sign_type'] = {'type' : 'string', 'value' : self.sign_type}
        prop_data['ref_crosswalk_id'] = {'type' : 'string', 'value' :  self.ref_crosswalk_id}
        
 
        return prop_data
    
    def to_dict(self):
        """json 파일 등으로 저장할 수 있는 dict 데이터로 변경한다"""
    
        dict_data = {
            'idx': self.idx,
            'points': self.pointToList(self.points),
            'sign_type':self.sign_type,
            'ref_crosswalk_id': self.ref_crosswalk_id,
            'link_id_list': self.link_id_list,
        }
        return dict_data
    
    @staticmethod
    def from_dict(dict_data, link_set=None):
        """json 파일등으로부터 읽은 dict 데이터에서 Signal 인스턴스를 생성한다"""

        """STEP #1 파일 내 정보 읽기"""
      
        idx = dict_data['idx']
        points = dict_data['points']
        sign_type = dict_data['sign_type']
        ref_crosswalk_id = dict_data['ref_crosswalk_id']
        link_id_list = []
        if 'link_id_list' in dict_data:
            link_id_list = dict_data['link_id_list']
        

        """STEP #2 인스턴스 생성"""
        obj = SingleCrosswalk(points, idx)
        obj.ref_crosswalk_id = ref_crosswalk_id
        obj.sign_type = sign_type
        obj.link_id_list = link_id_list

        return obj
        
    
    def isList(self, val):
        try:
            list(val)
            return True
        except ValueError:
            return False

    def pointToList(self, points):
        return_points = []
        for point in points:
            point_list = point.tolist() if type(point) != list else point
            return_points.append(point_list)

        return return_points

    def create_mesh_gen_points_bike_crosswalk(self, line, solid_line_interval=0.5):
        
        line.mesh_gen_vertices = []
        line.mesh_gen_vertex_subsets_for_each_face = []
        line.mesh_gen_vertex_uv_coords = [] # uv 좌표
        # 
        point_step = 0.1
        # 실선일 때
        solid_only_step = int(solid_line_interval/point_step)
        below_exec = False
        # 점선일 때는 다음의 계산이 필요
        dash_interval_L1 = line.dash_interval_L1
        dash_interval_L2 = line.dash_interval_L2
        L1L2 = dash_interval_L1 + dash_interval_L2
        if L1L2 == 0.0:
            return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords

        # 남는 길이를 계산하고, 이를 다시 적당히 분배해야 한다 (dashed line일 때만 계산한다)
        total_length = len(line.points) * point_step
        total_num_set = int(np.floor(total_length / L1L2))
        if total_num_set == 0: # delta 계산을 위해 total_num_set으로 나눠야하므로 계산 필요
            return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords
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
        while i < len(line.points):
            """STEP #01 vertex 생성을 위해 현재 lane marking에서 수직한 벡터 계산"""
            # solid쪽으로 좀 더 붙어야함
            add_point = np.array([(line.double_line_interval / 2.0), 0, 0])
            if line.lane_shape[0] == 'Broken':
                add_point = np.array([-(line.double_line_interval / 2.0), 0, 0])
            # 현재 위치에서의 벡터 계산
            if i == len(line.points) - 1: # 마지막 값이면, 이전 값과의 차이로 계산
                vect = line.points[i] - line.points[i-1]
            else:
                vect = line.points[i+1] - line.points[i]
            vect = vect / np.linalg.norm(vect, ord=2)

            # 현재 벡터를 xy평면상에서 +-90deg 회전시킨다.
            pos_vect_ccw = line.rorate_around_z_axis(np.pi/2, vect)
            pos_vect_cw = line.rorate_around_z_axis(-np.pi/2, vect)
            
            # 여기서 z값은 그냥 0으로 한다
            pos_vect_ccw[2] = 0
            pos_vect_cw[2] = 0


            """STEP #02 Mesh 생성을 위한 vertex 생성하기"""
            # 위 아래로 width/2 위/아래로 움직이면 된다.
            pos_vect_ccw1 = pos_vect_ccw * (line.double_line_interval / 4.0 + line.lane_width)
            pos_vect_ccw2 = pos_vect_ccw * (line.double_line_interval / 4.0)
            pos_vect_cw1 = pos_vect_cw * (line.double_line_interval / 4.0)
            pos_vect_cw2 = pos_vect_cw * (line.double_line_interval / 4.0 + line.lane_width)

            # 이를 현재 위치에서 더해주면 된다. 이 때 numpy array가 아닌 일반 list로 저장한다 (vtk에서 numpy array 지원X)
            up1 = (line.points[i] - add_point + pos_vect_ccw1).tolist()
            up2 = (line.points[i] - add_point + pos_vect_ccw2).tolist()
            dn1 = (line.points[i] - add_point + pos_vect_cw1).tolist()
            dn2 = (line.points[i] - add_point + pos_vect_cw2).tolist()

            line.mesh_gen_vertices.append(up1)
            line.mesh_gen_vertices.append(up2)
            line.mesh_gen_vertices.append(dn1)
            line.mesh_gen_vertices.append(dn2)

            line.mesh_gen_vertex_uv_coords.append([uv_idx, 0])
            line.mesh_gen_vertex_uv_coords.append([uv_idx, 1]) 
            line.mesh_gen_vertex_uv_coords.append([uv_idx, 0])
            line.mesh_gen_vertex_uv_coords.append([uv_idx, 1])

            uv_idx += 6

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

                if line.lane_shape[0] == 'Solid' or paint: # solid 일 때는 항상 paint = True이므로, lane_shape는 신경쓰지 않아도 된다.
                    line.mesh_gen_vertex_subsets_for_each_face.append(face1)

                if line.lane_shape[1] == 'Solid' or paint:
                    line.mesh_gen_vertex_subsets_for_each_face.append(face2)

            face_cnt += 1 # face_cnt는 실제 paint를 칠한 것 여부와 관계없이 증가
            paint = not paint # paint 칠했으면 다음번엔 칠하지 않아야하므로 토글  
            
        return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords
    
    def create_mesh_gen_points_crosswalk(self, line, link=None, solid_line_interval=0.5):
        # 방향... 링크와 수평하게 만들어야 함
        heading_vect = None
        if link is not None:
            if len(link.from_node.from_links) > 0:
                heading_vect = link.from_node.from_links[0].points[-1] - link.from_node.from_links[0].points[-2]
            else:
                heading_vect = link.points[-1] - link.points[-2]
            heading_vect = heading_vect / np.linalg.norm(heading_vect, ord=2)
        line.mesh_gen_vertices = []
        line.mesh_gen_vertex_subsets_for_each_face = []
        line.mesh_gen_vertex_uv_coords = [] # uv 좌표

        point_step = 0.1
        line.calculate_evenly_spaced_link_points(point_step)

        # 실선일 때
        solid_only_step = int(solid_line_interval/point_step)
        lane_width_count = int(line.lane_width/point_step)

        below_exec = False

        dash_interval_L1 = line.dash_interval_L1
        dash_interval_L2 = line.dash_interval_L2
        L1L2 = dash_interval_L1 + dash_interval_L2
        if L1L2 == 0.0:
            return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords

        # 남는 길이를 계산하고, 이를 다시 적당히 분배해야 한다
        total_length = len(line.points) * point_step
        total_num_set = int(np.floor(total_length / L1L2))
        if total_num_set == 0: # delta 계산을 위해 total_num_set으로 나눠야하므로 계산 필요
            return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords
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
        

        slice_count = -1
        while i < len(line.points):
            """STEP #01 vertex 생성을 위해 현재 lane marking에서 수직한 벡터 계산"""
            # 현재 위치에서의 벡터 계산
            if i == len(line.points) - 1:                   # 마지막 값이면, 이전 값과의 차이로 계산
                vect = line.points[i] - line.points[i-1]
            elif i != 0 and i < len(line.points) - 1:       # 중간 각을 위해 앞, 뒤 벡터 를 이용하여 계산.
                vect = line.points[i+1] - line.points[i-1]
            else:                                           # index = 0
                vect = line.points[i+1] - line.points[i]
            vect = vect / np.linalg.norm(vect, ord=2)

            rotation_radians = np.pi/2
            # lane_boundary 방향에 맞춰서 회전시키는 것 추가
            # if heading_vect is not None:
            #     dot_prod = np.inner(vect, heading_vect)
            #     rotation_radians = np.arccos(dot_prod)
            #     if rotation_radians < np.pi/2:
            #         rotation_radians = np.pi - rotation_radians

            # 현재 벡터를 xy평면상에서 +-90deg 회전시킨다.
            pos_vect_ccw = line.rorate_around_z_axis(rotation_radians, vect)
            pos_vect_cw = line.rorate_around_z_axis(rotation_radians-np.pi, vect)
            
            # 여기서 z값은 그냥 0으로 한다
            pos_vect_ccw[2] = 0
            pos_vect_cw[2] = 0

            pos_vect_ccw = (pos_vect_ccw * line.lane_width / 2.0)
            pos_vect_cw = (pos_vect_cw * line.lane_width / 2.0)

            # 이를 현재 위치에서 더해주면 된다. 이 때 numpy array가 아닌 일반 list로 저장한다 (vtk에서 numpy array 지원X)
            up = (line.points[i] + pos_vect_ccw).tolist()
            dn = (line.points[i] + pos_vect_cw).tolist()

            line.mesh_gen_vertices.append(up)
            line.mesh_gen_vertices.append(dn)

            """ Case #B 단선, 점선인 경우"""
            if paint:
                # 이번에 페인트 칠을 하는거라면, 페인트 칠해야하는 구간인 L1만큼 앞으로 나간다
                i += dashed_step_L1
            else: 
                # 페인트 칠을 하지 않고 건너뛰는 거면, L2만큼 앞으로 나간다
                i += dashed_step_L2

            """STEP #03 위에서 생성한 vertex로 face를 만들기 위한 vertex 조합을 생성한다"""
            if face_cnt > 0: # 첫번째 loop에는 하지 않기 위함
                if paint:
                    # face_cnt = 1 일 때, [0, 1, 3, 2]
                    # face_cnt = 2 일 때, [2, 3, 5, 4]
                    start_id = (face_cnt - 1) * 2
                    face = [start_id, start_id+1, start_id+3, start_id+2]

                    line.mesh_gen_vertex_subsets_for_each_face.append(face)

            """UV index 지정한다."""
            # uv 인덱스의 간격은 fix되면 프로젝트에서 계속 유지되어야 하므로, 협의하여 정합니다.
            line.mesh_gen_vertex_uv_coords.append([uv_idx, 0])
            line.mesh_gen_vertex_uv_coords.append([uv_idx, lane_width_count])
            
            if paint:
                uv_idx = 0
            else:
                uv_idx = 6

            face_cnt += 1 # face_cnt는 실제 paint를 칠한 것 여부와 관계없이 증가
            paint = not paint # paint 칠했으면 다음번엔 칠하지 않아야하므로 토글

        return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords


    def create_mesh_gen_points_crosswalk_double(self, line, link=None, solid_line_interval=0.5):
        # 방향... 링크와 수평하게 만들어야 함
        heading_vect = None
        if link is not None:
            if len(link.from_node.from_links) > 0:
                heading_vect = link.from_node.from_links[0].points[-1] - link.from_node.from_links[0].points[-2]
            else:
                heading_vect = link.points[-1] - link.points[-2]
            heading_vect = heading_vect / np.linalg.norm(heading_vect, ord=2)

        line.mesh_gen_vertices = []
        line.mesh_gen_vertex_subsets_for_each_face = []
        line.mesh_gen_vertex_uv_coords = [] # uv 좌표

        point_step = 0.1
        line.calculate_evenly_spaced_link_points(point_step)

        # 실선일 때
        solid_only_step = int(solid_line_interval/point_step)
        lane_width_count = int(line.lane_width/point_step)

        below_exec = False

        dash_interval_L1 = line.dash_interval_L1
        dash_interval_L2 = line.dash_interval_L2
        L1L2 = dash_interval_L1 + dash_interval_L2
        if L1L2 == 0.0:
            return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords

        # 남는 길이를 계산하고, 이를 다시 적당히 분배해야 한다
        total_length = len(line.points) * point_step
        total_num_set = int(np.floor(total_length / L1L2))
        if total_num_set == 0: # delta 계산을 위해 total_num_set으로 나눠야하므로 계산 필요
            return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords
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
        

        slice_count = -1
        while i < len(line.points):
            """STEP #01 vertex 생성을 위해 현재 lane marking에서 수직한 벡터 계산"""
            # 현재 위치에서의 벡터 계산
            if i == len(line.points) - 1:                   # 마지막 값이면, 이전 값과의 차이로 계산
                vect = line.points[i] - line.points[i-1]
            elif i != 0 and i < len(line.points) - 1:       # 중간 각을 위해 앞, 뒤 벡터 를 이용하여 계산.
                vect = line.points[i+1] - line.points[i-1]
            else:                                           # index = 0
                vect = line.points[i+1] - line.points[i]
            vect = vect / np.linalg.norm(vect, ord=2)

            rotation_radians = np.pi/2
            # lane_boundary 방향에 맞춰서 회전시키는 것 추가
            # if heading_vect is not None:
            #     dot_prod = np.inner(vect, heading_vect)
            #     rotation_radians = np.arccos(dot_prod)
            #     if rotation_radians < np.pi/2:
            #         rotation_radians = np.pi - rotation_radians

            # 현재 벡터를 xy평면상에서 +-90deg 회전시킨다.
            pos_vect_ccw = line.rorate_around_z_axis(rotation_radians, vect)
            pos_vect_cw = line.rorate_around_z_axis(rotation_radians-np.pi, vect)
            
            # 여기서 z값은 그냥 0으로 한다
            pos_vect_ccw[2] = 0
            pos_vect_cw[2] = 0

            pos_vect_ccw = (pos_vect_ccw * line.lane_width / 2.0)
            pos_vect_cw = (pos_vect_cw * line.lane_width / 2.0)

            # 이를 현재 위치에서 더해주면 된다. 이 때 numpy array가 아닌 일반 list로 저장한다 (vtk에서 numpy array 지원X)
            up1 = (line.points[i] + pos_vect_ccw).tolist()
            dn1 = (line.points[i]).tolist()

            up2 = (line.points[i] + vect*line.dash_interval_L1).tolist()
            dn2 = (line.points[i] + vect*line.dash_interval_L1 + pos_vect_cw).tolist()

            line.mesh_gen_vertices.append(up1)
            line.mesh_gen_vertices.append(dn1)

            line.mesh_gen_vertices.append(up2)
            line.mesh_gen_vertices.append(dn2)

            """ Case #B 단선, 점선인 경우"""
            if paint:
                # 이번에 페인트 칠을 하는거라면, 페인트 칠해야하는 구간인 L1만큼 앞으로 나간다
                i += dashed_step_L1
            else: 
                # 페인트 칠을 하지 않고 건너뛰는 거면, L2만큼 앞으로 나간다
                i += dashed_step_L2

            """STEP #03 위에서 생성한 vertex로 face를 만들기 위한 vertex 조합을 생성한다"""
            if face_cnt > 0: # 첫번째 loop에는 하지 않기 위함
                if paint:
                    # face_cnt = 1 일 때, [0, 1, 3, 2]
                    # face_cnt = 2 일 때, [2, 3, 5, 4]
                    start_id = (face_cnt - 1) * 4
                    face1 = [start_id+0, start_id+1, start_id+5, start_id+4]
                    face2 = [start_id+2, start_id+3, start_id+7, start_id+6]
                    line.mesh_gen_vertex_subsets_for_each_face.append(face1)
                    line.mesh_gen_vertex_subsets_for_each_face.append(face2)

            """UV index 지정한다."""
            # uv 인덱스의 간격은 fix되면 프로젝트에서 계속 유지되어야 하므로, 협의하여 정합니다.
            # indexss = int(np.floor((line.lane_width/2.0)/point_step))
            line.mesh_gen_vertex_uv_coords.append([uv_idx, 0])
            line.mesh_gen_vertex_uv_coords.append([uv_idx, 1])
            line.mesh_gen_vertex_uv_coords.append([uv_idx, 0])
            line.mesh_gen_vertex_uv_coords.append([uv_idx, 1])

            if paint:
                uv_idx = 0
            else:
                uv_idx = 6

            face_cnt += 1 # face_cnt는 실제 paint를 칠한 것 여부와 관계없이 증가
            paint = not paint # paint 칠했으면 다음번엔 칠하지 않아야하므로 토글

        return line.mesh_gen_vertices, line.mesh_gen_vertex_subsets_for_each_face, line.mesh_gen_vertex_uv_coords
