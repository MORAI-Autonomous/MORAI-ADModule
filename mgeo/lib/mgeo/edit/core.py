import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog

# MGeo Module
from class_defs import *
from save_load import *
from mesh_gen import * 
from utils import *

# from lib.path_planning.dijkstra import Dijkstra
from .core_search_funcs import *
from .core_select_funcs import *
from .funcs import *
from tasks.create_line_task import *
from tasks.create_junction_task import *
from tasks.delete_line_task import *
from tasks.delete_link_task import *
from tasks.delete_node_task import *
from tasks.path_planning_using_dijkstra_task import *


class MGeoEditCore:
    def __init__(self):
        # origin
        self.origin = None

        # Geometry Sets
        # 처음에는 default ctor를 호출하여 내부의 값이 빈 인스턴스를 갖게 해주어야
        # EditCore 클래스를 가져다 사용하는 쪽에서 line_set, node_set 등에 접근하는 함수를 에러없이
        # 호출할 수 있다. (이게 없으면 가져다 쓰는 쪽에서 None을 계속 체크해야 함)

        self.mgeo_planner_map = MGeoPlannerMap(NodeSet(), LineSet(), JunctionSet(), SignalSet(), SignalSet())

        # 항상 이 값이 관리된다
        # self.select_by_node = True >> 이건 self.select_func.select_by_node로 변경
        self.select_func = MGeoEditCoreSelectFunc()

        # Edit Func (OK / Cancel 을 호출하기 위함)
        self.edit_func = None
        self.edit_func_desc = ''

        # 각각의 Edit 기능을 담당하는 클래스
        self.create_line_func = CreateLineTask(self.mgeo_planner_map.link_set)
        self.create_junction_func = CreateJunctionTask(self.mgeo_planner_map.junction_set)
        self.path_planning_using_dijkstra_func = PathPlanningUsingDijkstraTask(
            self.mgeo_planner_map.node_set,
            self.mgeo_planner_map.link_set)


    def set_origin(self, origin):
        self.mgeo_planner_map.local_origin_in_global = origin


    def get_origin(self):
        return self.mgeo_planner_map.local_origin_in_global


    def set_geometry_obj(self, mgeo_planner_map):
        if type(mgeo_planner_map.node_set).__name__ != 'NodeSet':
            raise BaseException('An invalid variable passed to node_set. (expected type: NodeSet, passed variable type: {})'.format(type(mgeo_planner_map.node_set)))
        if type(mgeo_planner_map.link_set).__name__ != 'LineSet':
            raise BaseException('An invalid variable passed to line_set. (expected type: LineSet, passed variable type: {})'.format(type(mgeo_planner_map.link_set)))      
        if mgeo_planner_map.sign_set is not None:
            if type(mgeo_planner_map.sign_set).__name__ != 'SignalSet':
                raise BaseException('An invalid variable passed to ts_set. (expected type: SignalSet, passed variable type: {})'.format(type(mgeo_planner_map.sign_set)))
        if mgeo_planner_map.light_set is not None:
            if type(mgeo_planner_map.light_set).__name__ != 'SignalSet':
                raise BaseException('An invalid variable passed to tl_set. (expected type: SignalSet, passed variable type: {})'.format(type(mgeo_planner_map.light_set)))
        
        self.mgeo_planner_map = mgeo_planner_map

        # TODO(sglee): 필요한건가?        
        self.ref_points = self.mgeo_planner_map.link_set.get_ref_points()
        self.current_selected_point_idx_in_ref_point = None

        self.select_func.set_geometry_obj(
            self.mgeo_planner_map.node_set,
            self.mgeo_planner_map.link_set,
            self.mgeo_planner_map.sign_set,
            self.mgeo_planner_map.light_set
        )


    def set_node(self, node_set, origin=None):
        if type(node_set).__name__ != 'NodeSet':
            raise BaseException('An invalid variable passed to node_set. (expected type: NodeSet, passed variable type: {})'.format(type(node_set)))
        
        if self.mgeo_planner_map.local_origin_in_global is None:
            self.set_origin(origin)

        self.mgeo_planner_map.node_set = node_set
        self.select_func.set_node(self.mgeo_planner_map.node_set)


    def set_line(self, line_set):
        if type(line_set).__name__ != 'LineSet':
            raise BaseException('An invalid variable passed to line_set. (expected type: LineSet, passed variable type: {})'.format(type(line_set)))

        self.mgeo_planner_map.link_set = line_set
        self.select_func.set_line(self.mgeo_planner_map.link_set)

        # TODO(sglee): 필요한건가?        
        self.ref_points = self.mgeo_planner_map.link_set.get_ref_points()
        self.current_selected_point_idx_in_ref_point = None


    def set_ts(self, ts_set):
        if type(ts_set).__name__ != 'SignalSet':
            raise BaseException('An invalid variable passed to ts_set. (expected type: SignalSet, passed variable type: {})'.format(type(ts_set)))

        self.mgeo_planner_map.sign_set = ts_set
        self.select_func.set_ts(self.mgeo_planner_map.sign_set)


    def set_tl(self, tl_set):
        if type(tl_set).__name__ != 'SignalSet':
            raise BaseException('An invalid variable passed to tl_set. (expected type: SignalSet, passed variable type: {})'.format(type(tl_set)))

        self.mgeo_planner_map.light_set = tl_set
        self.select_func.set_tl(self.mgeo_planner_map.light_set)


    def set_junction(self, junction_set):
        self.mgeo_planner_map.junction_set = junction_set


    def reset_edit_mode(self):
        self.edit_func = None
        self.edit_func_desc = ''


    def set_multistep_edit_mode(self, edit_mode):
        self.edit_mode = edit_mode

        if edit_mode == 'create_line':
            # Create New Instance
            self.create_line_func = CreateLineTask(self.mgeo_planner_map.link_set)

            self.edit_func = self.create_line_func
            self.edit_func_desc = 'Create a line or link (connect two nodes)'

        elif edit_mode == 'create_junction':
            # Create New Instance
            self.create_junction_func = CreateJunctionTask(self.mgeo_planner_map.junction_set)

            
            self.edit_func = self.create_junction_func
            self.edit_func_desc = 'Create a junction from multiple nodes'

        elif edit_mode == 'dijkstra':
            # Create New Instance
            self.path_planning_using_dijkstra_func = PathPlanningUsingDijkstraTask(
                self.mgeo_planner_map.node_set,
                self.mgeo_planner_map.link_set)

            self.edit_func = self.path_planning_using_dijkstra_func
            self.edit_func_desc = 'Solve path planning problem using dijkstra function'


        else:
            raise BaseException('Undefined edit_mode name. (You passed = {})'.format(edit_mode))


    def get_multistep_edit_mode(self):
        return self.edit_mode


    def edit_mode_ok(self):
        ret = self.edit_func.do()
        self.reset_edit_mode()
        return ret


    def edit_mode_cancel(self):
        self.edit_func.cancel()
        self.reset_edit_mode()
        return 

    
    def get_onestep_edit_task(self, task):
        if task == 'delete_line':
            return DeleteLineTask(self.mgeo_planner_map.link_set)

        elif task == 'delete_link':
            return DeleteLinkTask(self.mgeo_planner_map.link_set)

        elif task == 'delete_node':
            return DeleteNodeTask(self.mgeo_planner_map.node_set)

        else:
            raise BaseException('Undefined edit_mode name. (You passed = {})'.format(edit_mode))

        
    def convert_ref_to_id(self, ref_list):
        id_list = []
        for v in ref_list:
            id_list.append(v.idx)

        return id_list


    def convert_id_to_ref_for_node(self, id_list, all_node_list):
        node_list = []
        for idx in id_list:
            if idx in all_node_list.nodes:
                node_list.append(all_node_list.nodes[idx])
            else:
                raise BaseException('Cannot find node with id in all_node_list')

        return node_list


    def convert_id_to_ref_for_link(self, id_list, all_link_list):
        link_list = []
        for idx in id_list:
            if idx in all_link_list.lines:
                link_list.append(all_link_list.lines[idx])
            else:
                raise BaseException('Cannot find link with id in all_link_list')

        return link_list


    def convert_id_to_ref_for_junction(self, id_list, all_junction_list):
        junction_list = []
        for idx in id_list:
            if idx in all_junction_list.junctions:
                junction_list.append(all_junction_list.junctions[idx])
            else:
                raise BaseException('Cannot find junction with id in all_junction_list')

        return junction_list


    def delete_node(self, node_set, node):
        edit_node.delete_node(node_set, node)


    def delete_nodes(self, node_set, delete_node_set):
        edit_node.delete_nodes(node_set, delete_node_set)


    def delete_link(self, link_set, link):
        edit_link.delete_link(link_set, link)


    def delete_signal(self, signal_set, signal):
        edit_signal.delete_signal(signal_set, signal)
