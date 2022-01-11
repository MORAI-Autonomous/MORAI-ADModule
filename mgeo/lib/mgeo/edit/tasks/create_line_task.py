import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

# MGeo Module
from class_defs import *

import numpy as np


class CreateLineTask:
    def __init__(self, line_set):
        self.start_node = None
        self.end_node = None  
        self.line_set = line_set

    def set_start_node(self, node):
        self.start_node = node
    
    def get_start_node(self, node):
        return self.start_node

    def set_end_node(self, node):
        self.end_node = node

    def get_end_node(self, node):
        return self.end_node

    def clear_nodes_selected(self):
        self.start_node = None
        self.end_node = None

    def cancel(self):
        self.clear_nodes_selected()

    def do(self, create_line_mode='link_edit', connector_length=0):
        if self.start_node is None:
            raise BaseException('Start node is not specified')

        if self.end_node is None:
            raise BaseException('End node is not specified')

        new_line = CreateLineTask.create_a_line(
            self.start_node, self.end_node, self.line_set,
            create_line_mode, connector_length)

        self.created_line = new_line

    def undo(self):
        MGeoEditCoreDeleteLine.remove_a_line()

    @staticmethod
    def create_a_line(start_node, end_node, line_set, create_line_mode, connector_length):
        """2개의 node를 연결한다
        create_line_mode: mesh 생성 모드인지 link 편집 모드인지를 구분
        """

        # link 수정모드인 경우에는 
        # 방향이 맞는지 체크한다
        # 방향이 틀리면 오류를 발생시킨다.
            
        # # 원하는 상황은
        # # start_point가 end이고
        # # end_point가 start인 경우이다
        # if self.create_line_mode == 1:
        #     if self.start_point['type'] != 'end' or self.end_point['type'] != 'start':
        #         print_warn('[ERROR] A new connecting link cannot be created. Check the direction again!')
        #         return

        if create_line_mode == 'mesh_creation':
            ''' Mesh Creation Mode'''
            # unit vector로 fill line 만들면 점의 숫자가 너무 많아져 vector 크기를 조정
            # 가능하도록 step_len 변수 추가
            step_len = connector_length

            vect_s_to_e = end_node.point - start_node.point
            mag = np.linalg.norm(vect_s_to_e, ord=2) # 벡터의 크기 계산
            unit_vect = vect_s_to_e / mag
            step_vect = step_len * unit_vect
            cnt = (int)(np.floor(mag / step_len))

            connecting_line = Line()
            connecting_line.create_the_first_point(start_node.point)
            connecting_line.create_points_from_current_pos_using_step(
                xyz_step_size=step_vect,
                step_num=cnt)
            
            # new_end point는 mag와 step_len 관계에 따라 추가하지 않아도 되는 경우가 있다
            if mag % step_len == 0:
                # 우연히 magnitude가 step_len의 배수인 경우이다.
                # 이 경우, 이미 create_points_from... 메소드에 의해
                # new_end에 해당하는 point가 linkLine에 추가되었다
                pass
            else:
                connecting_line.add_new_points(end_node.point)        

            # 이 라인의 from_node, to_node 설정해주기
            connecting_line.set_from_node(start_node)
            connecting_line.set_to_node(end_node)
        
        else:
            """ Link Edit Mode """
            # 가정: 두 점이 충분히 가까워서, 중간에 point를 생성할 필요가 없다.
            connecting_line = Link()
            points = np.vstack((start_node.point,end_node.point))
            connecting_line.set_points(points)

            # 이 라인의 from_node, to_node 설정해주기
            connecting_line.set_from_node(start_node)
            connecting_line.set_to_node(end_node)

        # line_set_object에 저장해주기 
        line_set.append_line(connecting_line, create_new_key=True)

        # TODO(sglee): ref_points가 더 이상 의미가 있나?
        # self.ref_points = self.line_set.get_ref_points()


