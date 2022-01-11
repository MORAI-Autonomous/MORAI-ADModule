import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../class_defs')))

from class_defs import *
from mgeo_planner_map import MGeoPlannerMap 

def merge_mgeo(first_mgeo_folder_path, second_mgeo_folder_path, result_path):   
    mgeo_planner_map_first = MGeoPlannerMap.create_instance_from_json(first_mgeo_folder_path)
    mgeo_planner_map_second = MGeoPlannerMap.create_instance_from_json(second_mgeo_folder_path)
    mgeo_planner_map_result = MGeoPlannerMap()

    for key in mgeo_planner_map_first.light_set.signals:
        if key in mgeo_planner_map_second.light_set.signals:
            print(key, mgeo_planner_map_second.light_set.signals[key])

    mgeo_planner_map_result.node_set.nodes = {**mgeo_planner_map_first.node_set.nodes, **mgeo_planner_map_second.node_set.nodes}
    mgeo_planner_map_result.link_set.lines = {**mgeo_planner_map_first.link_set.lines, **mgeo_planner_map_second.link_set.lines}
    mgeo_planner_map_result.light_set.signals = {**mgeo_planner_map_first.light_set.signals, **mgeo_planner_map_second.light_set.signals}

    mgeo_planner_map_result.to_json(result_path)

    return

if __name__ == u'__main__':
    first_mgeo_folder_path = 'C:\Projects\ModelMaker\saved\Stryx_Merge_New\First'
    second_mgeo_folder_path = 'C:\Projects\ModelMaker\saved\Stryx_Merge_New\Second'
    result_path = 'C:\Projects\ModelMaker\saved\Stryx_Merge_New\Merge'
    merge_mgeo(first_mgeo_folder_path, second_mgeo_folder_path, result_path)
