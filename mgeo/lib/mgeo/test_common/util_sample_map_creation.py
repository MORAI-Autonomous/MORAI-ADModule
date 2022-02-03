import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../'))) # mgeo가 있는 경로를 추가한다.

from class_defs import *
from save_load import mgeo_load
from save_load import mgeo_save

import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog

import test_cases_planner_map as test_case
import utils.lane_change_link_creation as lane_ch_link_creation

'''
Planner용 맵을 직접 생성하고 (plot을 통해서 확인)
이를 저장 혹은 로드하는 스크립트이다.
'''


def test_save(test_case_num=1):
    # [USER_OPTION]
    fill_in_points = False
    create_lane_change_link = False

    lane_set = LaneMarkingSet()
    lane_node_set = NodeSet()        
    # 초기 node_set, link_set 생성
    if test_case_num == 1:
        node_set, link_set = test_case.load_test_case_001()
    elif test_case_num == 2:
        node_set, link_set = test_case.load_test_case_002()
    elif test_case_num == 3:
        node_set, link_set = test_case.load_test_case_003()
    elif test_case_num == 100:
        node_set, link_set = test_case.load_test_case_100()
    elif test_case_num == 200:
        node_set, link_set = test_case.load_test_case_200()
    elif test_case_num == 300:
        node_set, link_set = test_case.load_test_case_300()        
    elif test_case_num == 400:
        node_set, link_set, lane_set, lane_node_set = test_case.load_test_case_400() 
    elif test_case_num == 500:
        node_set, link_set = test_case.load_test_case_500() 
    else:
        raise BaseException('ERROR: test case not defined for this test_case_num value.')


    # 일반 링크 내부를 일정한 간격으로 채워줄 것인가?
    if fill_in_points:
        for key, link in link_set.lines.items():
            link.fill_in_points_evenly(0.5)

    # 이제 차선 변경을 표현하는 링크를 생성한다
    if create_lane_change_link:
        lane_ch_link_set = lane_ch_link_creation.create_lane_change_link(link_set, 3)

        # 기존 link_set에 합친다
        LineSet.merge_two_sets(link_set, lane_ch_link_set)

    if create_lane_change_link:
        lane_ch_link_set = lane_ch_link_creation.create_lane_change_link(lane_set, 3)

        # 기존 link_set에 합친다
        lane_set.merge_two_sets(lane_set, lane_ch_link_set)


    # plot해서 확인하기 
    plt.figure()
    node_set.draw_plot(plt.gca())
    link_set.draw_plot(plt.gca())
    lane_node_set.draw_plot(plt.gca())
    lane_set.draw_plot(plt.gca())
    plt.show()

    # 이를 바탕으로 mgeo_planner_map을 생성
    mgeo_planner_map = MGeoPlannerMap(node_set, link_set, lane_set, lane_node_set )

    # 저장하기
    output_path = '../../../output/'
    output_path = os.path.join(current_path, output_path)
    output_path = os.path.normpath(output_path)

    save_path = filedialog.askdirectory(
        initialdir = output_path, 
        title = 'Save in the folder below') # defaultextension = 'json') 과 같은거 사용 가능    
    
    mgeo_planner_map.to_json(save_path)
    # mgeo_save.save_node_and_link(save_path, node_set, link_set)
    

def test_load():
    #
    input_path = '../../../saved/'
    input_path = os.path.join(current_path, input_path)
    input_path = os.path.normpath(input_path)

    load_path = filedialog.askdirectory(
        initialdir = input_path, 
        title = 'Load files from') # defaultextension = 'json') 과 같은거 사용 가능 

    mgeo_planner_map = MGeoPlannerMap.create_instance_from_json(load_path)

    # plot해서 확인하기 
    plt.figure()
    mgeo_planner_map.node_set.draw_plot(plt.gca())
    mgeo_planner_map.link_set.draw_plot(plt.gca())
    plt.show()

if __name__ == u'__main__':
    test_save(test_case_num=500)
    # test_load()