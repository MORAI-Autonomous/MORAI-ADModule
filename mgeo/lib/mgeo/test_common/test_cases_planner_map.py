import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../'))) # mgeo가 있는 경로를 추가한다.

from class_defs import *

import numpy as np
import matplotlib.pyplot as plt


def add_lane_ch_info_no_existing_links(link_set, lane_change_info):
        '''
        존재하는 링크에 차선 변경으로 진입 가능한 링크를 표현해준다
        '''
        i = 0
        for idx, src_line in link_set.lines.items():
            dbf_rec = lane_change_info[i]
            
            if dbf_rec['L_LinkID'] != '':
                dst_line = link_set.lines[dbf_rec['L_LinkID']]
                src_line.set_left_lane_change_dst_link(dst_line)
            
            if dbf_rec['R_LinkID'] != '':
                dst_line = link_set.lines[dbf_rec['R_LinkID']]
                src_line.set_right_lane_change_dst_link(dst_line)
    
            i += 1


def load_test_case_001():
    '''
    직선으로 3개 그어진 링크 A,B,C를 생성한다
    그리고 각 링크 사이의 차선 변경으로 진입 가능 여부를 dbf rec와 유사한 형태로 생성한다
    '''

    link_set = LineSet() 
    node_set = NodeSet()

    node = Node(0)
    node.point = np.array([0, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(1)
    node.point = np.array([5, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(2)
    node.point = np.array([10, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(3)
    node.point = np.array([0, 50, 0])
    node_set.nodes[node.idx] = node

    node = Node(4)
    node.point = np.array([5, 50, 0])
    node_set.nodes[node.idx] = node 

    node = Node(5)
    node.point = np.array([10, 50, 0])
    node_set.nodes[node.idx] = node

    node = Node(6)
    node.point = np.array([15, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(7)
    node.point = np.array([15, 50, 0])
    node_set.nodes[node.idx] = node


    link = Link(idx='A')
    link.set_points_using_node(node_set.nodes[0], node_set.nodes[3], step_len=1)
    link_set.lines[link.idx] = link

    link = Link(idx='B')
    link.set_points_using_node(node_set.nodes[1], node_set.nodes[4], step_len=1)
    link_set.lines[link.idx] = link

    link = Link(idx='C')
    link.set_points_using_node(node_set.nodes[2], node_set.nodes[5], step_len=1)
    link_set.lines[link.idx] = link

    link = Link(idx='D')
    link.set_points_using_node(node_set.nodes[6], node_set.nodes[7], step_len=1)
    link_set.lines[link.idx] = link

    lane_change_info = [ 
        {'L_LinkID': '', 'R_LinkID': 'B'},
        {'L_LinkID': 'A', 'R_LinkID': 'C'},
        {'L_LinkID': 'B', 'R_LinkID': 'D'},
        {'L_LinkID': 'C', 'R_LinkID': ''}]

    # 아래를 실행하고 나면 각 링크에 lane_ch 정보까지 생성이 되었다
    add_lane_ch_info_no_existing_links(link_set, lane_change_info)

    return node_set, link_set


def load_test_case_002():
    node_set = NodeSet() 
    link_set = LineSet()

    """
    노드 정의하기
    """
    node = Node(0)
    node.point = np.array([0, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(1)
    node.point = np.array([10, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(2)
    node.point = np.array([30, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(3)
    node.point = np.array([0, 10, 0])
    node_set.nodes[node.idx] = node

    node = Node(4)
    node.point = np.array([10, 10, 0])
    node_set.nodes[node.idx] = node 

    node = Node(5)
    node.point = np.array([30, 10, 0])
    node_set.nodes[node.idx] = node

    node = Node(6)
    node.point = np.array([0, 15, 0])
    node_set.nodes[node.idx] = node

    node = Node(7)
    node.point = np.array([10, 15, 0])
    node_set.nodes[node.idx] = node

    node = Node(8)
    node.point = np.array([30, 15, 0])
    node_set.nodes[node.idx] = node



    """
    특정 노드에서 특정 노드로 가는 각각의 선을 정의
    """
    # line0
    link = Link(idx=0)
    link.set_points_using_node(node_set.nodes[0], node_set.nodes[1], 1)
    link_set.lines[link.idx] = link

    # line1
    link = Link(idx=1)
    link.set_points_using_node(node_set.nodes[1], node_set.nodes[2], 1)
    link_set.lines[link.idx] = link

    # line2
    link = Link(idx=2)
    link.set_points_using_node(node_set.nodes[0], node_set.nodes[3], 1)
    link_set.lines[link.idx] = link

    # line3
    link = Link(idx=3)
    link.set_points_using_node(node_set.nodes[1], node_set.nodes[4], 1)
    link_set.lines[link.idx] = link

    # line4
    link = Link(idx=4)
    link.set_points_using_node(node_set.nodes[2], node_set.nodes[5], 1)
    link_set.lines[link.idx] = link

    # line5
    link = Link(idx=5)
    link.set_points_using_node(node_set.nodes[3], node_set.nodes[4], 1)
    link_set.lines[link.idx] = link

    # line6
    link = Link(idx=6)
    link.set_points_using_node(node_set.nodes[4], node_set.nodes[5], 1)
    link_set.lines[link.idx] = link

    # line7
    link = Link(idx=7)
    link.set_points_using_node(node_set.nodes[3], node_set.nodes[6], 1)
    link_set.lines[link.idx] = link

    # line8
    link = Link(idx=8)
    link.set_points_using_node(node_set.nodes[4], node_set.nodes[7], 1)
    link_set.lines[link.idx] = link

    # line9
    link = Link(idx=9)
    link.set_points_using_node(node_set.nodes[5], node_set.nodes[8], 1)
    link_set.lines[link.idx] = link
    
    # line10
    link = Link(idx=10)
    link.set_points_using_node(node_set.nodes[6], node_set.nodes[7], 1)
    link_set.lines[link.idx] = link

    # line11
    link = Link(idx=11)
    link.set_points_using_node(node_set.nodes[7], node_set.nodes[8], 1)
    link_set.lines[link.idx] = link

    return node_set, link_set


def load_test_case_003():
    '''
    남쪽으로 진행하는 도로
    3.75m 1개 - 3.5m 3개 - 3.75m 1개

    
    '''
    node_set = NodeSet()
    link_set = LineSet()
    
    """
    노드 정의하기
    """

    # 1차선이 동쪽에 있다
    x1 = 3.5 * 1.5 + 3.75/2
    x2 = 3.5 
    x3 = 0
    x4 = -1 * x2
    x5 = -1 * x1
    y = -1000


    node = Node(0)
    node.point = np.array([x1, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(1)
    node.point = np.array([x2, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(2)
    node.point = np.array([x3, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(3)
    node.point = np.array([x4, 0, 0])
    node_set.nodes[node.idx] = node

    node = Node(4)
    node.point = np.array([x5, 0, 0])
    node_set.nodes[node.idx] = node



    node = Node(5)
    node.point = np.array([x1, y, 0])
    node_set.nodes[node.idx] = node

    node = Node(6)
    node.point = np.array([x2, y, 0])
    node_set.nodes[node.idx] = node

    node = Node(7)
    node.point = np.array([x3, y, 0])
    node_set.nodes[node.idx] = node

    node = Node(8)
    node.point = np.array([x4, y, 0])
    node_set.nodes[node.idx] = node

    node = Node(9)
    node.point = np.array([x5, y, 0])
    node_set.nodes[node.idx] = node



    node = Node(10)
    node.point = np.array([x1, 2*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(11)
    node.point = np.array([x2, 2*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(12)
    node.point = np.array([x3, 2*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(13)
    node.point = np.array([x4, 2*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(14)
    node.point = np.array([x5, 2*y, 0])
    node_set.nodes[node.idx] = node



    node = Node(15)
    node.point = np.array([x1, 3*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(16)
    node.point = np.array([x2, 3*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(17)
    node.point = np.array([x3, 3*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(18)
    node.point = np.array([x4, 3*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(19)
    node.point = np.array([x5, 3*y, 0])
    node_set.nodes[node.idx] = node



    node = Node(20)
    node.point = np.array([x1, 4*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(21)
    node.point = np.array([x2, 4*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(22)
    node.point = np.array([x3, 4*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(23)
    node.point = np.array([x4, 4*y, 0])
    node_set.nodes[node.idx] = node

    node = Node(24)
    node.point = np.array([x5, 4*y, 0])
    node_set.nodes[node.idx] = node



    link = Link(idx='L00', link_type='6')
    link.set_points_using_node(node_set.nodes[0], node_set.nodes[5], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L01', link_type='6')
    link.set_points_using_node(node_set.nodes[1], node_set.nodes[6], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L02', link_type='6')
    link.set_points_using_node(node_set.nodes[2], node_set.nodes[7], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L03', link_type='6')
    link.set_points_using_node(node_set.nodes[3], node_set.nodes[8], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L04', link_type='6')
    link.set_points_using_node(node_set.nodes[4], node_set.nodes[9], step_len=20)
    link_set.lines[link.idx] = link


    link = Link(idx='L05', link_type='6')
    link.set_points_using_node(node_set.nodes[5], node_set.nodes[10], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L06', link_type='6')
    link.set_points_using_node(node_set.nodes[6], node_set.nodes[11], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L07', link_type='6')
    link.set_points_using_node(node_set.nodes[7], node_set.nodes[12], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L08', link_type='6')
    link.set_points_using_node(node_set.nodes[8], node_set.nodes[13], step_len=20)
    link_set.lines[link.idx] = link
    
    link = Link(idx='L09', link_type='6')
    link.set_points_using_node(node_set.nodes[9], node_set.nodes[14], step_len=20)
    link_set.lines[link.idx] = link


    link = Link(idx='L10', link_type='6')
    link.set_points_using_node(node_set.nodes[10], node_set.nodes[15], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L11', link_type='6')
    link.set_points_using_node(node_set.nodes[11], node_set.nodes[16], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L12', link_type='6')
    link.set_points_using_node(node_set.nodes[12], node_set.nodes[17], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L13', link_type='6')
    link.set_points_using_node(node_set.nodes[13], node_set.nodes[18], step_len=20)
    link_set.lines[link.idx] = link
    
    link = Link(idx='L14', link_type='6')
    link.set_points_using_node(node_set.nodes[14], node_set.nodes[19], step_len=20)
    link_set.lines[link.idx] = link


    link = Link(idx='L15', link_type='6')
    link.set_points_using_node(node_set.nodes[15], node_set.nodes[20], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L16', link_type='6')
    link.set_points_using_node(node_set.nodes[16], node_set.nodes[21], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L17', link_type='6')
    link.set_points_using_node(node_set.nodes[17], node_set.nodes[22], step_len=20)
    link_set.lines[link.idx] = link

    link = Link(idx='L18', link_type='6')
    link.set_points_using_node(node_set.nodes[18], node_set.nodes[23], step_len=20)
    link_set.lines[link.idx] = link
    
    link = Link(idx='L19', link_type='6')
    link.set_points_using_node(node_set.nodes[19], node_set.nodes[24], step_len=20)
    link_set.lines[link.idx] = link

    lane_change_info = [ 
        {'L_LinkID': '', 'R_LinkID': 'B'},
        {'L_LinkID': 'A', 'R_LinkID': 'C'},
        {'L_LinkID': 'B', 'R_LinkID': 'D'},
        {'L_LinkID': 'C', 'R_LinkID': ''}]

    return node_set, link_set


def load_test_case_100():
    """
    lane section 2개로 구성된, Road 1개를 생성할 수 있는 링크 구성
    MGeo 내 좌표계 상 남 -> 북으로 진행하는 도로
    """

    node_set = NodeSet()
    link_set = LineSet()

    # 각 차선 위치
    x1 = 0
    x2 = 5


    # 1차선용 노드
    node = Node('000')
    node.point = np.array([x1, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('001')
    node.point = np.array([x1, 100, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('002')
    node.point = np.array([x1, 200, 0])
    node_set.append_node(node, create_new_key=False)


    # 2차선용 노드
    node = Node('100')
    node.point = np.array([x2, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('101')
    node.point = np.array([x2, 100, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('102')
    node.point = np.array([x2, 200, 0])
    node_set.append_node(node, create_new_key=False)


    link = Link(idx='000', link_type='6')
    link.set_points_using_node(node_set.nodes['000'], node_set.nodes['001'], step_len=20)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='001', link_type='6')
    link.set_points_using_node(node_set.nodes['001'], node_set.nodes['002'], step_len=20)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)


    link = Link(idx='100', link_type='6')
    link.set_points_using_node(node_set.nodes['100'], node_set.nodes['101'], step_len=20)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='101', link_type='6')
    link.set_points_using_node(node_set.nodes['101'], node_set.nodes['102'], step_len=20)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)


    link_set.lines['000'].lane_ch_link_right = link_set.lines['100']
    link_set.lines['100'].lane_ch_link_left = link_set.lines['000']

    link_set.lines['001'].lane_ch_link_right = link_set.lines['101']
    link_set.lines['101'].lane_ch_link_left = link_set.lines['001']

    return node_set, link_set


def load_test_case_200():
    """
    lane section 2개로 구성된, Road 1개를 생성할 수 있는 링크 구성
    MGeo 내 좌표계 상 남 -> 북으로 진행하는 도로
    """

    node_set = NodeSet()
    link_set = LineSet()


    node = Node('000')
    node.point = np.array([1, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('001')
    node.point = np.array([5, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('002')
    node.point = np.array([9, 0, 0])
    node_set.append_node(node, create_new_key=False)


    #
    node = Node('100')
    node.point = np.array([1, 10, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('101')
    node.point = np.array([5, 10, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('102')
    node.point = np.array([10, 10, 0])
    node_set.append_node(node, create_new_key=False)


    #
    node = Node('200')
    node.point = np.array([0, 20, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('201')
    node.point = np.array([5, 20, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('202')
    node.point = np.array([10, 20, 0])
    node_set.append_node(node, create_new_key=False)


    #
    node = Node('300')
    node.point = np.array([-1, 30, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('301')
    node.point = np.array([4, 30, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('302')
    node.point = np.array([8, 30, 0])
    node_set.append_node(node, create_new_key=False)


    link = Link(idx='000', link_type='6')
    link.set_points_using_node(node_set.nodes['000'], node_set.nodes['100'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='001', link_type='6')
    link.set_points_using_node(node_set.nodes['001'], node_set.nodes['101'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='002', link_type='6')
    link.set_points_using_node(node_set.nodes['002'], node_set.nodes['102'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)


    link = Link(idx='100', link_type='6')
    link.set_points_using_node(node_set.nodes['100'], node_set.nodes['200'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='101', link_type='6')
    link.set_points_using_node(node_set.nodes['101'], node_set.nodes['201'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='102', link_type='6')
    link.set_points_using_node(node_set.nodes['102'], node_set.nodes['202'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)


    link = Link(idx='200', link_type='6')
    link.set_points_using_node(node_set.nodes['200'], node_set.nodes['300'], step_len=2.5)
    link.road_id = '001'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='201', link_type='6')
    link.set_points_using_node(node_set.nodes['201'], node_set.nodes['301'], step_len=2.5)
    link.road_id = '001'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='202', link_type='6')
    link.set_points_using_node(node_set.nodes['202'], node_set.nodes['302'], step_len=2.5)
    link.road_id = '001'
    link_set.append_line(link, create_new_key=False)


    link_set.lines['000'].lane_ch_link_right = link_set.lines['001']
    link_set.lines['001'].lane_ch_link_left = link_set.lines['000']

    link_set.lines['001'].lane_ch_link_right = link_set.lines['002']
    link_set.lines['002'].lane_ch_link_left = link_set.lines['002']

    link_set.lines['100'].lane_ch_link_right = link_set.lines['101']
    link_set.lines['101'].lane_ch_link_left = link_set.lines['100']

    link_set.lines['101'].lane_ch_link_right = link_set.lines['102']
    link_set.lines['102'].lane_ch_link_left = link_set.lines['101']

    link_set.lines['200'].lane_ch_link_right = link_set.lines['201']
    link_set.lines['201'].lane_ch_link_left = link_set.lines['200']

    link_set.lines['201'].lane_ch_link_right = link_set.lines['202']
    link_set.lines['202'].lane_ch_link_left = link_set.lines['201']

    return node_set, link_set


def load_test_case_300():
    """
    lane section 2개로 구성된, Road 1개를 생성할 수 있는 링크 구성
    MGeo 내 좌표계 상 남 -> 북으로 진행하는 도로
    """

    node_set = NodeSet()
    link_set = LineSet()


    node = Node('N000')
    node.point = np.array([0, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N001')
    node.point = np.array([4, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N002')
    node.point = np.array([9, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N003')
    node.point = np.array([15, 0, 0])
    node_set.append_node(node, create_new_key=False)


    node = Node('N100')
    node.point = np.array([0, 10, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N101')
    node.point = np.array([4, 10, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N102')
    node.point = np.array([9, 10, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N103')
    node.point = np.array([15, 10, 0])
    node_set.append_node(node, create_new_key=False)


    # node = Node('N200')
    # node.point = np.array([0, 20, 0])
    # node_set.append_node(node, create_new_key=False)

    node = Node('N201')
    node.point = np.array([4, 20, 0])
    node_set.append_node(node, create_new_key=False)

    # node = Node('N202')
    # node.point = np.array([9, 20, 0])
    # node_set.append_node(node, create_new_key=False)

    # node = Node('N203')
    # node.point = np.array([15, 20, 0])
    # node_set.append_node(node, create_new_key=False)


    # node = Node('N300')
    # node.point = np.array([0, 30, 0])
    # node_set.append_node(node, create_new_key=False)

    node = Node('N301')
    node.point = np.array([4, 30, 0])
    node_set.append_node(node, create_new_key=False)

    # node = Node('N302')
    # node.point = np.array([9, 30, 0])
    # node_set.append_node(node, create_new_key=False)

    # node = Node('N303')
    # node.point = np.array([15, 30, 0])
    # node_set.append_node(node, create_new_key=False)


    # node = Node('N400')
    # node.point = np.array([0, 40, 0])
    # node_set.append_node(node, create_new_key=False)

    node = Node('N401')
    node.point = np.array([4, 40, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N402')
    node.point = np.array([9, 40, 0])
    node_set.append_node(node, create_new_key=False)

    # node = Node('N403')
    # node.point = np.array([15, 40, 0])
    # node_set.append_node(node, create_new_key=False)


    # node = Node('N500')
    # node.point = np.array([0, 50, 0])
    # node_set.append_node(node, create_new_key=False)

    node = Node('N501')
    node.point = np.array([4, 50, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N502')
    node.point = np.array([9, 50, 0])
    node_set.append_node(node, create_new_key=False)

    # node = Node('N503')
    # node.point = np.array([15, 50, 0])
    # node_set.append_node(node, create_new_key=False)


    link = Link(idx='L000', link_type='6')
    link.set_points_using_node(node_set.nodes['N000'], node_set.nodes['N100'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='L001', link_type='6')
    link.set_points_using_node(node_set.nodes['N001'], node_set.nodes['N101'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='L002', link_type='6')
    link.set_points_using_node(node_set.nodes['N002'], node_set.nodes['N102'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='L003', link_type='6')
    link.set_points_using_node(node_set.nodes['N003'], node_set.nodes['N103'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link_set.lines['L000'].lane_ch_link_right = link_set.lines['L001']
    link_set.lines['L001'].lane_ch_link_left = link_set.lines['L000']

    link_set.lines['L001'].lane_ch_link_right = link_set.lines['L002']
    link_set.lines['L002'].lane_ch_link_left = link_set.lines['L001']

    link_set.lines['L002'].lane_ch_link_right = link_set.lines['L003']
    link_set.lines['L003'].lane_ch_link_left = link_set.lines['L002']


    link = Link(idx='L101', link_type='6')
    link.set_points_using_node(node_set.nodes['N101'], node_set.nodes['N201'], step_len=2.5)
    link.road_id = '100'
    link_set.append_line(link, create_new_key=False)


    link = Link(idx='L201', link_type='6')
    link.set_points_using_node(node_set.nodes['N201'], node_set.nodes['N301'], step_len=2.5)
    link.road_id = '200'
    link_set.append_line(link, create_new_key=False)    


    link = Link(idx='L301', link_type='6')
    link.set_points_using_node(node_set.nodes['N301'], node_set.nodes['N401'], step_len=2.5)
    link.road_id = '300'
    link_set.append_line(link, create_new_key=False)   


    link = Link(idx='L401', link_type='6')
    link.set_points_using_node(node_set.nodes['N401'], node_set.nodes['N501'], step_len=2.5)
    link.road_id = '400'
    link_set.append_line(link, create_new_key=False)    

    link = Link(idx='L402', link_type='6')
    link.set_points_using_node(node_set.nodes['N402'], node_set.nodes['N502'], step_len=2.5)
    link.road_id = '400'
    link_set.append_line(link, create_new_key=False)    

    link_set.lines['L401'].lane_ch_link_right = link_set.lines['L402']
    link_set.lines['L402'].lane_ch_link_left = link_set.lines['L401']


    return node_set, link_set


def load_test_case_400():
    """
    lane section 2개로 구성된, Road 1개를 생성할 수 있는 링크 구성
    MGeo 내 좌표계 상 남 -> 북으로 진행하는 도로
    """

    node_set = NodeSet()
    link_set = LineSet()

    lanemarking_set = LaneMarkingSet()

    lane_node_set = NodeSet()

    node = Node('L000')
    node.point = np.array([-3, 0, 0])
    lane_node_set.append_node(node, create_new_key=False)

    node = Node('L001')
    node.point = np.array([-3, 15, 0])
    lane_node_set.append_node(node, create_new_key=False)

    node = Node('L002')
    node.point = np.array([-3, 30, 0])
    lane_node_set.append_node(node, create_new_key=False)

    node = Node('L003')
    node.point = np.array([-3, 50, 0])
    lane_node_set.append_node(node, create_new_key=False)

    lane = LaneMarking(idx = '100')
    lane.set_points_using_node(lane_node_set.nodes['L000'], lane_node_set.nodes['L003'], step_len=2.5)
    lane.lane_code = '1'
    lanemarking_set.append_lane(lane, create_new_key=False)

    node = Node('N000')
    node.point = np.array([0, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N001')
    node.point = np.array([4, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N002')
    node.point = np.array([9, 0, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N003')
    node.point = np.array([15, 0, 0])
    node_set.append_node(node, create_new_key=False)


    node = Node('N100')
    node.point = np.array([0, 10, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N101')
    node.point = np.array([4, 10, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N102')
    node.point = np.array([9, 10, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N103')
    node.point = np.array([15, 10, 0])
    node_set.append_node(node, create_new_key=False)


    # node = Node('N200')
    # node.point = np.array([0, 20, 0])
    # node_set.append_node(node, create_new_key=False)

    node = Node('N201')
    node.point = np.array([4, 20, 0])
    node_set.append_node(node, create_new_key=False)

    # node = Node('N202')
    # node.point = np.array([9, 20, 0])
    # node_set.append_node(node, create_new_key=False)

    # node = Node('N203')
    # node.point = np.array([15, 20, 0])
    # node_set.append_node(node, create_new_key=False)


    # node = Node('N300')
    # node.point = np.array([0, 30, 0])
    # node_set.append_node(node, create_new_key=False)

    node = Node('N301')
    node.point = np.array([4, 30, 0])
    node_set.append_node(node, create_new_key=False)

    # node = Node('N302')
    # node.point = np.array([9, 30, 0])
    # node_set.append_node(node, create_new_key=False)

    # node = Node('N303')
    # node.point = np.array([15, 30, 0])
    # node_set.append_node(node, create_new_key=False)


    # node = Node('N400')
    # node.point = np.array([0, 40, 0])
    # node_set.append_node(node, create_new_key=False)

    node = Node('N401')
    node.point = np.array([4, 40, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N402')
    node.point = np.array([9, 40, 0])
    node_set.append_node(node, create_new_key=False)

    # node = Node('N403')
    # node.point = np.array([15, 40, 0])
    # node_set.append_node(node, create_new_key=False)


    # node = Node('N500')
    # node.point = np.array([0, 50, 0])
    # node_set.append_node(node, create_new_key=False)

    node = Node('N501')
    node.point = np.array([4, 50, 0])
    node_set.append_node(node, create_new_key=False)

    node = Node('N502')
    node.point = np.array([9, 50, 0])
    node_set.append_node(node, create_new_key=False)

    # node = Node('N503')
    # node.point = np.array([15, 50, 0])
    # node_set.append_node(node, create_new_key=False)


    link = Link(idx='L000', link_type='6')
    link.set_points_using_node(node_set.nodes['N000'], node_set.nodes['N100'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='L001', link_type='6')
    link.set_points_using_node(node_set.nodes['N001'], node_set.nodes['N101'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='L002', link_type='6')
    link.set_points_using_node(node_set.nodes['N002'], node_set.nodes['N102'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link = Link(idx='L003', link_type='6')
    link.set_points_using_node(node_set.nodes['N003'], node_set.nodes['N103'], step_len=2.5)
    link.road_id = '000'
    link_set.append_line(link, create_new_key=False)

    link_set.lines['L000'].lane_ch_link_right = link_set.lines['L001']
    link_set.lines['L001'].lane_ch_link_left = link_set.lines['L000']

    link_set.lines['L001'].lane_ch_link_right = link_set.lines['L002']
    link_set.lines['L002'].lane_ch_link_left = link_set.lines['L001']

    link_set.lines['L002'].lane_ch_link_right = link_set.lines['L003']
    link_set.lines['L003'].lane_ch_link_left = link_set.lines['L002']


    link = Link(idx='L101', link_type='6')
    link.set_points_using_node(node_set.nodes['N101'], node_set.nodes['N201'], step_len=2.5)
    link.road_id = '100'
    link_set.append_line(link, create_new_key=False)


    link = Link(idx='L201', link_type='6')
    link.set_points_using_node(node_set.nodes['N201'], node_set.nodes['N301'], step_len=2.5)
    link.road_id = '200'
    link_set.append_line(link, create_new_key=False)    


    link = Link(idx='L301', link_type='6')
    link.set_points_using_node(node_set.nodes['N301'], node_set.nodes['N401'], step_len=2.5)
    link.road_id = '300'
    link_set.append_line(link, create_new_key=False)   


    link = Link(idx='L401', link_type='6')
    link.set_points_using_node(node_set.nodes['N401'], node_set.nodes['N501'], step_len=2.5)
    link.road_id = '400'
    link_set.append_line(link, create_new_key=False)    

    link = Link(idx='L402', link_type='6')
    link.set_points_using_node(node_set.nodes['N402'], node_set.nodes['N502'], step_len=2.5)
    link.road_id = '400'
    link_set.append_line(link, create_new_key=False)    

    link_set.lines['L401'].lane_ch_link_right = link_set.lines['L402']
    link_set.lines['L402'].lane_ch_link_left = link_set.lines['L401']


    return node_set, link_set, lanemarking_set, lane_node_set

def load_test_case_500():

    node_set = NodeSet()
    link_set = LineSet()

    half_width = 4.72504 / 2
    
    for i in range(-5, 6):
       for j in range(-4, 4):
           node = Node()
           node.point = np.array([half_width + half_width*2*j, i * 500 , 0])
           node_set.append_node(node, create_new_key=True)

    index = 0 
    
    while(index < 10):
        for i in range(0, 8):
             link = Link()
             nodeName1 = 'ND'+'{0:06d}'.format(i + (index*8))
             nodeName2 = 'ND'+'{0:06d}'.format(i + (index*8) + 8)
             if nodeName1 in node_set.nodes and nodeName2 in node_set.nodes:
                 link.set_points_using_node(node_set.nodes[nodeName1], node_set.nodes[nodeName2], step_len=2.5)
                 link.road_id = '000'
                 link_set.append_line(link, create_new_key=True)
                 
        index = index+1

    return node_set, link_set


