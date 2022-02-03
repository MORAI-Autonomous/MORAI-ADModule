import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

# MGeo Module
from class_defs import *

import numpy as np


class DeleteAllUsingXYRangeTask:
    def __init__(self, node_set, link_set, ts_set, tl_set):
        pass
    