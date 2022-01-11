
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

from class_defs import *
import utils.lane_change_link_creation as lane_ch_link_creation

import numpy as np
import matplotlib.pyplot as plt
import test_cases_planner_map as test_case


# TODO(sglee): 아래와 같은 구조를 참고하여 같은 구조 사용하고 있던 곳 삭제해야 
# def test_method1_create_lane_change_links(link_set, lane_change_info):
#     lane_ch_link_set = LineSet() 

#     i = 0
#     # 

#     #원래 있는 item의 keyset을 받아와서 실행한다
#     keys = link_set.lines.keys()

#     for idx, src_line in link_set.lines.items():
#         dbf_rec = lane_change_info[i]
        
#         if dbf_rec['L_LinkID'] != '':
#             dst_line = link_set.lines[dbf_rec['L_LinkID']]
#             to_node = dst_line.get_to_node()
#             from_node = src_line.get_from_node()

#             idx = dbf_rec['L_LinkID'] + '-' + src_line.idx
#             lane_ch_line = Link(idx=idx, lazy_point_init=True)
#             lane_ch_line.set_points_using_node_lazy_init(to_node, from_node)
#             lane_ch_link_set.lines[lane_ch_line.idx] = lane_ch_line

        
#         if dbf_rec['R_LinkID'] != '':
#             dst_line = link_set.lines[dbf_rec['R_LinkID']]
#             to_node = dst_line.get_to_node()
#             from_node = src_line.get_from_node()

#             idx = dbf_rec['R_LinkID'] + '-' + src_line.idx
#             lane_ch_line = Link(idx=idx, lazy_point_init=True)
#             lane_ch_line.set_points_using_node_lazy_init(to_node, from_node)
#             lane_ch_link_set.lines[lane_ch_line.idx] = lane_ch_line
        
#         i += 1

#     return lane_ch_link_set


def func_test_main():
    node_set, link_set = test_case.load_test_case_001()

    # 이제 차선 변경을 표현하는 링크를 생성한다
    lane_ch_link_set = lane_ch_link_creation.create_lane_change_link(link_set, 3)

    # 
    LineSet.merge_two_sets(link_set, lane_ch_link_set)

    fig = plt.figure()
    node_set.draw_plot(plt.gca())
    link_set.draw_plot(plt.gca())

    for idx, src_line in lane_ch_link_set.lines.items():
        print('idx:', idx)

    plt.gca().axis('equal')
    fig.set_size_inches(8,8)
    plt.show()


import unittest


class TestLaneChangeLinkCreation(unittest.TestCase):
    def test_main(self):
        # 테스트 셋업
        node_set, link_set = test_case.load_test_case_001()
        
        # 테스트 함수
        lane_ch_link_set = lane_ch_link_creation.create_lane_change_link(link_set, 3)

        # 결과 체크: 차선 변경 1번인 링크
        self.assertTrue('A-B' in lane_ch_link_set.lines)
        self.assertTrue('B-A' in lane_ch_link_set.lines)

        self.assertTrue('B-C' in lane_ch_link_set.lines)
        self.assertTrue('C-B' in lane_ch_link_set.lines)

        self.assertTrue('C-D' in lane_ch_link_set.lines)
        self.assertTrue('D-C' in lane_ch_link_set.lines)

        # 결과 체크: 차선 변경 2번인 링크
        self.assertTrue('A-C' in lane_ch_link_set.lines)
        self.assertTrue('C-A' in lane_ch_link_set.lines)

        self.assertTrue('B-D' in lane_ch_link_set.lines)
        self.assertTrue('D-B' in lane_ch_link_set.lines)

        # test: 차선 변경 3번인 링크
        self.assertTrue('A-D' in lane_ch_link_set.lines)
        self.assertTrue('D-A' in lane_ch_link_set.lines)
        
     


if __name__ == u'__main__':
    func_test_main()
    # unittest.main()