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


def test_load():
    file_path = os.path.join(current_path, 'temp')
    node_set, line_set = mgeo_load.load(file_path)

    plt.figure()
    node_set.draw_plot(plt.gca())
    line_set.draw_plot(plt.gca())
    plt.show()


if __name__ == u'__main__':
    test_load()