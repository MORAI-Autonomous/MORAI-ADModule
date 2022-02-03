import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../../')))

import numpy as np

import edit_node
import edit_link
import edit_lane_marking

from utils import error_fix


def delete_objects_out_of_xy_range(mgeo_planner_map, xlim, ylim, hard=True):
    node_set = mgeo_planner_map.node_set
    link_set = mgeo_planner_map.link_set
    ts_set = mgeo_planner_map.sign_set
    tl_set = mgeo_planner_map.light_set
    sm_set = mgeo_planner_map.sm_set
    jc_set = mgeo_planner_map.junction_set

    lane_node_set = mgeo_planner_map.lane_node_set
    lane_marking_set = mgeo_planner_map.lane_marking_set
    
    
    links_to_remove = list()
    for idx, item in link_set.lines.items():
        if hard:
            # 조금이라도 벗어난 데이터는 삭제한다
            if not item.is_completely_included_in_xy_range(xlim, ylim):
                links_to_remove.append(item)
        else:
            # 조금이라도 걸쳐있는 데이터는 유지한다
            if item.is_out_of_xy_range(xlim, ylim):
                links_to_remove.append(item)

    for item in links_to_remove:

        # 해당 링크에 연결된 ts, tl을 우선 삭제한다
        for ts in item.get_traffic_signs():
            if ts.idx in ts_set.signals.keys():
                ts_set.signals.pop(ts.idx)
        for tl in item.get_traffic_lights():
            if tl.idx in tl_set.signals.keys():
                tl_set.signals.pop(tl.idx)
        for sm in item.get_surface_markings():
            if sm.idx in sm_set.data.keys():
                sm_set.data.pop(sm.idx)

        # 링크를 삭제한다
        edit_link.delete_link(link_set, item)


    # danling node 삭제하는 것으로 node는 해결
    nodes_to_remove = error_fix.find_dangling_nodes(node_set)
    for item in nodes_to_remove:
        edit_node.delete_node(node_set, item, delete_junction=True, junction_set=jc_set)


    # 이 범위에 들어오지 않는 데이터는 삭제한다 (TS)
    ts_to_remove = list()
    for idx, item in ts_set.signals.items():
        if item.is_out_of_xy_range(xlim, ylim):
            ts_to_remove.append(item)

    for item in ts_to_remove:
        ts_set.remove_signal(item)
    
    
    # 이 범위에 들어오지 않는 데이터는 삭제한다 (TL)
    tl_to_remove = list()
    for idx, item in tl_set.signals.items():
        if item.is_out_of_xy_range(xlim, ylim):
            tl_to_remove.append(item)

    for item in tl_to_remove:
        tl_set.remove_signal(item)


    # 이 범위에 들어오지 않는 데이터는 삭제한다 (SM)
    sm_to_remove = list()
    for idx, item in sm_set.data.items():
        if not item.is_completely_included_in_xy_range(xlim, ylim):
            sm_to_remove.append(item)

    for item in sm_to_remove:
        sm_set.remove_data(item)

    lanes_to_remove = list()
    for idx, item in lane_marking_set.lanes.items():
        if hard:
            # 조금이라도 벗어난 데이터는 삭제한다
            if not item.is_completely_included_in_xy_range(xlim, ylim):
                lanes_to_remove.append(item)
        else:
            # 조금이라도 걸쳐있는 데이터는 유지한다
            if item.is_out_of_xy_range(xlim, ylim):
                lanes_to_remove.append(item)
                
    for item in lanes_to_remove:
        edit_lane_marking.delete_lane(lane_marking_set, item)

    lane_nodes_to_remove = error_fix.find_dangling_nodes(lane_node_set)
    for item in lane_nodes_to_remove:
        edit_node.delete_node(lane_node_set, item, delete_junction=True, junction_set=jc_set)


def delete_object_inside_xy_range(mgeo_planner_map, xlim, ylim):
    node_set = mgeo_planner_map.node_set
    link_set = mgeo_planner_map.link_set
    ts_set = mgeo_planner_map.sign_set
    tl_set = mgeo_planner_map.light_set
    sm_set = mgeo_planner_map.sm_set
    jc_set = mgeo_planner_map.junction_set

    lane_node_set = mgeo_planner_map.lane_node_set
    lane_marking_set = mgeo_planner_map.lane_marking_set

    # 이 range에 완전히 들어오는 데이터는 삭제한다
    links_to_remove = list()
    for idx, item in link_set.lines.items():
        if item.is_completely_included_in_xy_range(xlim, ylim):
            links_to_remove.append(item)

    for item in links_to_remove:

        # 해당 링크에 연결된 ts, tl을 우선 삭제한다
        for ts in item.get_traffic_signs():
            if ts.idx in ts_set.signals.keys():
                ts_set.signals.pop(ts.idx)
        for tl in item.get_traffic_lights():
            if tl.idx in tl_set.signals.keys():
                tl_set.signals.pop(tl.idx)

        # 링크를 삭제한다      
        edit_link.delete_link(link_set, item)


    # danling node 삭제하는 것으로 node는 해결
    nodes_to_remove = error_fix.find_dangling_nodes(node_set)
    for item in nodes_to_remove:
        edit_node.delete_node(node_set, item, delete_junction=True, junction_set=jc_set)


    # 이 range에 들어오는 데이터만 남긴다 (TS)
    ts_to_remove = list()
    for idx, item in ts_set.signals.items():
        if not item.is_out_of_xy_range(xlim, ylim):
            ts_to_remove.append(item)

    for item in ts_to_remove:
        ts_set.remove_signal(item)
    

    # 이 range에 들어오는 데이터만 남긴다 (TL)
    tl_to_remove = list()
    for idx, item in tl_set.signals.items():
        if not item.is_out_of_xy_range(xlim, ylim):
            tl_to_remove.append(item)

    for item in tl_to_remove:
        tl_set.remove_signal(item)


    # 이 range에 들어오는 데이터만 남긴다 (SM)
    sm_to_remove = list()
    for idx, item in sm_set.data.items():
        if item.is_completely_included_in_xy_range(xlim, ylim):
            sm_to_remove.append(item)
    
    for item in sm_to_remove:
        sm_set.remove_data(item)

    lanes_to_remove = list()
    for idx, item in lane_marking_set.lanes.items():
        if item.is_completely_included_in_xy_range(xlim, ylim):
            lanes_to_remove.append(item)
                
    for item in lanes_to_remove:
        edit_lane_marking.delete_lane(lane_marking_set, item)

    lane_nodes_to_remove = error_fix.find_dangling_nodes(lane_node_set)
    for item in lane_nodes_to_remove:
        edit_node.delete_node(lane_node_set, item, delete_junction=True, junction_set=jc_set)


def change_origin(mgeo_planner_map, new_origin):
    # 연산을 위해 numpy array로 변경한다
    if not isinstance(new_origin, np.ndarray):
        new_origin = np.array(new_origin)

    old_origin = mgeo_planner_map.get_origin()

    # mgeo_planner_map 내부 item을 다음 값만큼 이동시켜야 한다
    diff = new_origin - old_origin

    # origin 값 변경
    mgeo_planner_map.set_origin(new_origin)

    # 모든 좌표 변경
    for idx, node in mgeo_planner_map.node_set.nodes.items():
        node.point = node.point - diff

    for idx, link in mgeo_planner_map.link_set.lines.items():
        link.points = link.points - diff
        link.set_points(link.points)

    for idx, ts in mgeo_planner_map.sign_set.signals.items():
        ts.point = ts.point - diff

    for idx, tl in mgeo_planner_map.light_set.signals.items():
        tl.point = tl.point - diff

    for idx, sm in mgeo_planner_map.sm_set.data.items():
        sm.points = sm.points - diff

        
    for idx, node in mgeo_planner_map.lane_node_set.nodes.items():
        node.point = node.point - diff

    for idx, lane in mgeo_planner_map.lane_marking_set.lanes.items():
        lane.points = lane.points - diff
        lane.set_points(lane.points)