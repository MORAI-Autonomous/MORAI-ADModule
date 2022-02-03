import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

# MGeo Module
from class_defs import *

import core_search_funcs as search


class MGeoEditCoreSelectFunc:
    def __init__(self):
        self.select_by_node = True
    
        self.selected_node = None
        self.selected_line = None
        self.selected_point = None

        self.node_set = None
        self.line_set = None
        self.ts_set = None
        self.tl_set = None


    def set_geometry_obj(self, node_set, line_set, ts_set=None, tl_set=None):
        if type(node_set).__name__ != 'NodeSet':
            raise BaseException('An invalid variable passed to node_set. (expected type: NodeSet, passed variable type: {})'.format(type(node_set)))
        if type(line_set).__name__ != 'LineSet':
            raise BaseException('An invalid variable passed to line_set. (expected type: LineSet, passed variable type: {})'.format(type(line_set)))
        if ts_set is not None:
            if type(ts_set).__name__ != 'SignalSet':
                raise BaseException('An invalid variable passed to ts_set. (expected type: Signal, passed variable type: {})'.format(type(ts_set)))
        if tl_set is not None:
            if type(tl_set).__name__ != 'SignalSet':
                raise BaseException('An invalid variable passed to tl_set. (expected type: Signal, passed variable type: {})'.format(type(tl_set)))
        self.node_set = node_set
        self.line_set = line_set
        self.ts_set = ts_set
        self.tl_set = tl_set


    def set_node(self, node_set):
        if type(node_set).__name__ != 'NodeSet':
            raise BaseException('An invalid variable passed to node_set. (expected type: NodeSet, passed variable type: {})'.format(type(node_set)))
        self.node_set = node_set


    def set_line(self, line_set):
        if type(line_set).__name__ != 'LineSet':
            raise BaseException('An invalid variable passed to line_set. (expected type: LineSet, passed variable type: {})'.format(type(line_set)))
        self.line_set = line_set


    def set_ts(self, ts_set):
        if type(ts_set).__name__ != 'SignalSet':
            raise BaseException('An invalid variable passed to ts_set. (expected type: Signal, passed variable type: {})'.format(type(ts_set)))
        self.ts_set = ts_set


    def set_tl(self, tl_set):
        if type(tl_set).__name__ != 'SignalSet':
            raise BaseException('An invalid variable passed to tl_set. (expected type: Signal, passed variable type: {})'.format(type(tl_set)))
        self.tl_set = tl_set


    def change_select_mode(self):
        if self.select_by_node is True:
            self.select_by_node = False
            _mode = 'point mode'

        elif self.select_by_node is False:
            self.select_by_node = True
            _mode = 'node mode'

        print('[INFO] Node selection mode changed to: {}'.format(_mode))


    def update_selected_objects_using_node_snap(self, search_coord):
        """좌표로부터 근처의 node를 찾고, 이를 이용하여 선택된 객체들을 업데이트한다"""

        # [STEP #1] Node 찾기
        closest_dist, selected_node =\
            search.find_nearest_point_node_base(self.node_set, search_coord)

        # [NOTE] 여기서 self.selected_node를 먼저 업데이트하면 안 된다!
        # 가장 마지막에 업데이트 해야 함


        # [STEP #2] Line/Link 찾기
        # 같은 노드를 다시 선택한거면, 현재 링크에 있는 다른 링크를 선택해준다
        if self.selected_node is selected_node:
            # 검색해야할 링크의 종류를 만든다
            to_links = selected_node.get_to_links()
            from_links = selected_node.get_from_links()
            related_links = to_links + from_links # 해당 노드에서 출발하는 링크를 먼저 검색

            def get_next_link(related_links, current_link):
                for i in range(len(related_links)):
                    if current_link is related_links[i]:
                        next_i = i + 1
                        if next_i == len(related_links):
                            next_i = 0
                        return related_links[next_i]

                # current_link가 None이거나 해서 related_link 내에서 못 찾으면
                # 그냥 첫번째 값으로
                next_i = 0
                return related_links[next_i]

            # 현재 선택되어 있던 링크 말고, 다음 링크를 선택해준다    
            self.selected_line = get_next_link(related_links, self.selected_line)
        else:
            # 그냥 다른 노드를 선택한 것이었으면,
            # 해당 노드에 있는 related_link 중 아무거나를 선택
            # to_links 또는 from_links 둘 중 하나가 [] 일 수 있기 때문에 이렇게 함
            to_links = selected_node.get_to_links()
            from_links = selected_node.get_from_links()
            related_links = to_links + from_links
            if len(related_links) == 0:
                print_warn('[ERROR] There are no links connected to this node')
                return 
            self.selected_line = related_links[0]


        # [STEP #3] Point 찾기
        # 같은 노드를 선택했을 때, 서로 다른 포인트가 선택될 수 있도록 하는 코드
        if self.selected_node is selected_node:
            # 루프의 경우 무조건 같은 포인트 선택되는걸 막아준다
            if self.selected_point['type'] == 'end':
                # 현재 선택된 포인트가 end 였으면, start 지점을 선택하게 해준다
                self.selected_point = self.selected_line.get_point_dict(0)
            elif self.selected_point['type'] == 'start':
                # 현재 선택된 포인트가 start 였으면, end 지점을 선택하게 해준다
                self.selected_point = self.selected_line.get_point_dict(-1)
            else:
                print_warn('[ERROR] Loop identification failed')
                return
        
        elif self.selected_line.get_from_node() is selected_node:
            self.selected_point = self.selected_line.get_point_dict(0)

        elif self.selected_line.get_to_node() is selected_node:
            self.selected_point = self.selected_line.get_point_dict(-1)
        
        else:
            raise BaseException('[ERROR] selected_node is not linked to the selected_line! (Not intended code flow)')

        # [STEP #4] Selected Node 업데이트 
        # NOTE: 가장 마지막에 해야 한다. 이보다 앞부분에 실행되는 코드에서 
        # 현재 선택한 노드가 그 전의 노드와 같은지 아닌지 확인하기 때문
        self.selected_node = selected_node
        return selected_node

    
    def update_selected_point(self, idx_move):
        if self.selected_line is None:
            print_warn('[ERROR] line_set must be set first!')
            return

        if self.selected_point != None:
            # line을 먼저 찾는다
            idx_line = self.selected_point['idx_line']
            self.selected_line = self.line_set.lines[idx_line]

            # idx point 값을 이동
            idx_point = self.selected_point['idx_point'] 
            idx_point += idx_move
            
            if idx_point < 0:
                idx_point = 0
            if idx_point > self.selected_line.get_last_idx():
                idx_point = self.selected_line.get_last_idx()
            
            # selected point 다시 얻고 업데이트하기
            self.selected_point = self.selected_line.get_point_dict(idx_point)