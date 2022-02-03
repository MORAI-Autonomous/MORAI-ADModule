import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../'))) # mgeo가 있는 경로를 추가한다.
sys.path.append(current_path + '/../../../') # mgeo가 있는 경로를 추가한다.

import matplotlib.pyplot as plt

from class_defs import *
from mgeo_editor_morai_mpl import mpl_user_input_handler
from edit import core
from test_common import test_cases_planner_map


def main():
    node_set, link_set = test_cases_planner_map.load_test_case_001()
    
    mgeo_planner_map = MGeoPlannerMap(node_set, link_set)
    edit_core = core.MGeoEditCore()
    edit_core.set_geometry_obj(mgeo_planner_map)

    ui_handler = mpl_user_input_handler.UserInputHandler(edit_core)
    ui_handler.start_simple_ui()
    print('END')

if __name__ == u'__main__':
    main()