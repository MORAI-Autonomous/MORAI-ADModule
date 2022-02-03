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


def test_save():
    import test_cases_mesh_gen_geometry
    node_set, line_set = test_cases_mesh_gen_geometry.load_test_case_001()
    
    plane_set = PlaneSet()
    
    output_path = os.path.join(current_path, 'temp')
    mgeo_save.save(output_path, node_set, line_set, plane_set)
    

if __name__ == u'__main__':
    test_save()