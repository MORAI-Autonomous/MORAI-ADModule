import os, sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

from class_defs.line import Line

class Path(Line):
    
    def __init__(self, id):
        self.start_point = dict()
        self.end_point = dict()
        self.stop_point = dict()
        self.link_path = list()
        # 각기 다른 method에 대한 id 부여
        self.path_id = id
    

