import math
from collections import defaultdict
import copy
from enum import Enum
from typing import DefaultDict, List, Tuple

from PyQt5.QtCore import right
import numpy
from lib.mgeo.class_defs.intersection_controller_set import IntersectionControllerSet
from lib.mgeo.class_defs.intersection_controller_set_builder import IntersectionInfo
from class_defs.signal import Signal
from class_defs.line_set import LineSet
from class_defs.link import Link
from class_defs.intersection_controller_set import IntersectionControllerSet


class Direction(Enum):
    Vertical = 1
    Horizontal = 2
    Error = 5


class Plane(Enum):
    Left = 1
    Right = 2
    Up = 3
    Down = 4
    Error = 5


class Abnormal(Enum):
    Normal = 1
    Link = 2
    Pedestrian_only = 3
    Both = 4


class SyncedTLInfo(object):
    def __init__(self) -> None:
        self.intscn_id: str = None
        self.synced_tl_idx: int = None
        self.link_list: List[Link] = None
        self.direction: Direction = None
        self.plane: Plane = None
        self.colors: List[str] = None
        self.abnormal_code: Abnormal = False
        self.is_bus: bool = False
        self.has_pedestrian: bool = False

    def set_idx(self, intscn_id, idx: int) -> 'SyncedTLInfo':
        self.intscn_id = intscn_id
        self.synced_tl_idx = idx
        return self

    def set_link(self, link_list: List[Link]) -> 'SyncedTLInfo':
        self.link_list = link_list
        return self

    def set_bus(self, tls_info: IntersectionInfo, synced_tl: List[str]) -> None:
        num_synced_tl = len(synced_tl)
        cnt_tl_bus = 0
        for tl in synced_tl:
            if tls_info.tl_dict[tl].type == 'bus':
                cnt_tl_bus += 1
        if num_synced_tl == cnt_tl_bus:
            self.is_bus = True
        return

    def set_ps(self, tls_info: IntersectionInfo, synced_tl: List[str]) -> None:
        for tl in synced_tl:
            if tls_info.tl_dict[tl].type == 'pedestrian':
                self.has_pedestrian = True
        return

    def set_direction(self, dir: Direction) -> 'SyncedTLInfo':
        self.direction = dir
        return self

    def set_plane(self, plane: Plane) -> 'SyncedTLInfo':
        self.plane = plane
        return self

    def set_colors(self, bulbs: List[str]) -> 'SyncedTLInfo':
        self.colors = copy.deepcopy(bulbs)
        return self

    def set_abnormal(self, code: Abnormal) -> 'SyncedTLInfo':
        self.abnormal_code = code
        return self


class SyncedTLState(object):
    def __init__(self) -> None:
        self.duration: int = None
        self.lightcolor: List[str] = None
        self.tl_bus: List[int] = []
        self.has_ps: bool = False

    def set_duration(self, time: int) -> 'SyncedTLState':
        self.duration = time
        return self

    def set_lightcolor(self, colors: List[str]) -> 'SyncedTLState':
        self.lightcolor = copy.deepcopy(colors)
        return self

    def set_bus(self, tl_id: List[int]) -> 'SyncedTLState':
        self.tl_bus.extend(tl_id)
        return self

    def set_ps(self, has_ps: bool) -> 'SyncedTLState':
        self.has_ps = has_ps
        return self

    def clone(self) -> None:
        return self

    @staticmethod
    def to_dict(obj: 'SyncedTLState'):
        return {"duration": obj.duration, "lightcolor": obj.lightcolor}


class IntersectionState(object):
    def __init__(self) -> None:
        self.intscn_id: str = None
        self.tl_state: List[SyncedTLState] = None
        self.yellow_duration: List[int] = [3]
        self.ps_state: List[List[int]] = []

    def set_intscn_id(self, id: str) -> None:
        self.intscn_id = id

    def set_state(self, states: List[SyncedTLState]) -> None:
        self.tl_state = self.__defined_all_red_state(states)
        self.__init_yellow_duration(self.tl_state)
        self.__set_ps_state(self.tl_state)

    def __defined_all_red_state(self, states: List[SyncedTLState]) -> List[SyncedTLState]:
        fixed_states: List[SyncedTLState] = []
        num_colors = len(states[0].lightcolor)
        all_red = ["R"] * num_colors
        for state in states:
            fixed_states.append(state)
            fixed_states.append(SyncedTLState().set_duration(3).set_lightcolor(all_red))

        return fixed_states

    def __init_yellow_duration(self, states: List[SyncedTLState]) -> None:
        self.yellow_duration = self.yellow_duration * len(states[0].lightcolor)

    def __set_ps_state(self, states: List[SyncedTLState]) -> None:
        ps_state = [0, 0, 0, 12, 15]
        visited = []
        for state_idx, state in enumerate(states):
            for synced_idx, synced_tl_signal in enumerate(state.lightcolor):
                if synced_idx in state.tl_bus:
                    continue
                if synced_idx in visited:
                    continue
                if synced_tl_signal == 'Undefined':
                    visited.append(synced_idx)
                    ps_state[0] = state_idx
                    ps_state[1] = synced_idx
                    self.ps_state.append(ps_state)
                    ps_state = [0, 0, 0, 12, 15]
                if synced_tl_signal == 'SG' or synced_tl_signal == 'G_with_GLeft':
                    visited.append(synced_idx)
                    ps_state[0] = state_idx
                    ps_state[1] = synced_idx
                    self.ps_state.append(ps_state)
                    ps_state = [0, 0, 0, 12, 15]

    @staticmethod
    def to_dict(obj):
        """json 파일등으로 저장할 수 있는 dict 데이터로 변경한다"""

        dict_data = {
            'idx': obj.intscn_id,
            'TLState': [state.to_dict(state) for state in obj.tl_state],
            'yelloduration': obj.yellow_duration,
            'PSState': obj.ps_state
        }

        return dict_data


class IntersectionStateBuilder(object):
    def __init__(self, intscn_ctrlr_set: IntersectionControllerSet, tls_info: IntersectionInfo,
                 link_set: LineSet) -> None:
        self.intscn_ctrlr_set: IntersectionControllerSet = intscn_ctrlr_set
        self.tls_info = tls_info
        self.link_set = link_set
        self.intscn_state_list: List[IntersectionState] = None
        self.abnormals: List[str] = None

    def build(self) -> Tuple[List[str], List[IntersectionState]]:
        intscn_configs, self.abnormals = self.detect_intscn_config_internal()
        self.intscn_state_list = self.make_tl_state_internal(intscn_configs)
        return self.abnormals, self.intscn_state_list

    def detect_intscn_config_internal(self) -> Tuple[DefaultDict[str, List[SyncedTLInfo]], List[str]]:
        intscn_config: DefaultDict[str, List[SyncedTLInfo]] = defaultdict(list)
        abnormal_config: List[str] = []
        for intscn_id, intscn_controllers in self.intscn_ctrlr_set.intersection_controllers.items():
            intscn_synced_list = intscn_controllers.TL
            for idx, synced_tl in enumerate(intscn_synced_list):
                synced_tl_info = SyncedTLInfo()
                direction, plane, abnormal_code = self.__detect_topology(synced_tl)
                if direction.value == Direction.Error.value or plane.value == Plane.Error.value:
                    abnormal_config.append(intscn_id)
                    continue
                if abnormal_code.value != Abnormal.Normal.value:
                    abnormal_config.append(intscn_id)
                bulb_colors = self.__detect_colors(synced_tl)
                synced_tl_info.set_idx(intscn_id, idx)
                synced_tl_info.set_link(self.tls_info.tl_dict[synced_tl[0]].link_list)
                synced_tl_info.set_bus(self.tls_info, synced_tl)
                synced_tl_info.set_ps(self.tls_info, synced_tl)
                synced_tl_info.set_direction(direction).set_plane(plane)
                synced_tl_info.set_colors(bulb_colors)
                synced_tl_info.set_abnormal(abnormal_code)
                intscn_config[intscn_id].append(synced_tl_info)

        return intscn_config, abnormal_config

    def __detect_topology(self, synced_tl: List[str]) -> Tuple[Direction, Plane, bool, Abnormal]:
        # is_ped_only = False
        abnormal_code = self.__is_abnormal(synced_tl)
        if abnormal_code.value == Abnormal.Pedestrian_only.value or \
                abnormal_code.value == Abnormal.Both.value:
            # is_ped_only = True
            for tl in synced_tl:
                tl_obj = self.tls_info.tl_dict[tl]
                current_link = self.__handle_right_link_only(tl_obj)
                if current_link is None:
                    current_link = self.link_set.lines[tl_obj.link_id_list[0]]
                roadway_dir = self.__get_direction(current_link)
                roadway_plane = self.__get_plane(current_link, roadway_dir)
                if roadway_dir.value != Direction.Error.value and \
                        roadway_plane.value != Plane.Error.value:
                    return roadway_dir, roadway_plane, Abnormal.Pedestrian_only
            return roadway_dir, roadway_plane, Abnormal.Pedestrian_only
        for tl in synced_tl:
            tl_obj = self.tls_info.tl_dict[tl]
            if len(tl_obj.link_list) == 0:
                return Direction.Error, Plane.Error, Abnormal.Link
            current_link = self.__get_straight_link_id(tl_obj)
            if current_link is None:  # 3-arm intersection
                current_link = self.__get_curved_link_id(tl_obj)
            roadway_dir = self.__get_direction(current_link)
            roadway_plane = self.__get_plane(current_link, roadway_dir)
            if roadway_dir.value != Direction.Error.value and \
                    roadway_plane.value != Plane.Error.value:
                return roadway_dir, roadway_plane, abnormal_code
        return roadway_dir, roadway_plane, abnormal_code

    def __is_abnormal(self, synced_tl: List[str]) -> Abnormal:
        cnt_ped = 0
        is_link_type_none = False
        is_ped_only = False
        for tl in synced_tl:
            for link in self.tls_info.tl_dict[tl].link_list:
                if link.link_type is None:
                    is_link_type_none = True
            if 'pedestrian' == self.tls_info.tl_dict[tl].type:
                cnt_ped += 1
        if cnt_ped == len(synced_tl):
            # return Abnormal.Pedestrian_only
            is_ped_only = True

        if is_link_type_none and is_ped_only:
            return Abnormal.Both
        elif is_ped_only:
            return Abnormal.Pedestrian_only
        elif is_link_type_none:
            return Abnormal.Link
        else:
            return Abnormal.Normal

    def __get_straight_link_id(self, tl_obj: Signal) -> Link:
        link_id_list = tl_obj.link_id_list
        for link_id in link_id_list:
            current_link = self.link_set.lines[link_id]
            if "straight" == current_link.related_signal:
                return current_link
            else:
                continue

    def __get_curved_link_id(self, tl_obj: Signal) -> Link:
        link_id_list = tl_obj.link_id_list
        for link_id in link_id_list:
            current_link = self.link_set.lines[link_id]
            if "left" == current_link.related_signal or \
                    "left_unprotected" == current_link.related_signal:
                return current_link
            else:
                continue
        for link_id in link_id_list:
            current_link = self.link_set.lines[link_id]
            if "right_unprotected" == current_link.related_signal:
                return current_link
            else:
                continue

    def __handle_right_link_only(self, tl_obj: Signal) -> Link:
        link_id_list = tl_obj.link_id_list
        for link_id in link_id_list:
            current_link = self.link_set.lines[link_id]
            if "right_unprotected" == current_link.related_signal:
                return current_link

    def __get_direction(self, link_obj: Link) -> Direction:
        pos_from_node = list(link_obj.points[0])
        pos_to_node = list(link_obj.points[-1])
        dx = abs(self.__get_dx(pos_from_node, pos_to_node))
        dy = abs(self.__get_dy(pos_from_node, pos_to_node))
        # left_unprotected, left will have direction of Vertical
        if link_obj.related_signal == 'left' or \
                link_obj.related_signal == 'left_unprotected':
            alpha = dx * 0.5
            if dy + alpha > dx:
                return Direction.Vertical
            else:
                return Direction.Horizontal

        if dy == dx:
            return Direction.Error
        elif dy > dx:
            return Direction.Vertical
        else:
            return Direction.Horizontal

    def __get_plane(self, link_obj: Link, direction: Direction) -> Plane:
        pos_from_node = list(link_obj.points[0])
        pos_to_node = list(link_obj.points[-1])
        dx = self.__get_dx(pos_from_node, pos_to_node)
        dy = self.__get_dy(pos_from_node, pos_to_node)
        if direction.value == Direction.Vertical.value:
            if dy > 0:
                return Plane.Left
            else:
                return Plane.Right
        elif direction.value == Direction.Horizontal.value:
            if dx > 0:
                return Plane.Up
            else:
                return Plane.Down

    def __get_dx(self, pos_from: List[float], pos_to: List[float]):
        idx_x = 0
        dy = pos_from[idx_x] - pos_to[idx_x]
        return dy

    def __get_dy(self, pos_from: List[float], pos_to: List[float]):
        idx_y = 1
        dy = pos_from[idx_y] - pos_to[idx_y]
        return dy

    def __detect_colors(self, synced_tl: List[str]) -> List[str]:
        for tl in synced_tl:
            tl_obj = self.tls_info.tl_dict[tl]
            colors = self.__get_related_signal(tl_obj)
            if colors.__len__() != 0:
                return colors

    def __get_related_signal(self, tl_obj: Signal) -> List[str]:
        bulb_colors = []
        link_id_list = tl_obj.link_id_list
        for link_id in link_id_list:
            current_link = self.link_set.lines[link_id]
            bulb = current_link.related_signal
            if bulb is None or bulb == 'right_unprotected':
                continue
            if bulb not in bulb_colors:
                bulb_colors.append(bulb)

        return bulb_colors

    def make_tl_state_internal(self, configs: DefaultDict[str, List[SyncedTLInfo]]) -> List[IntersectionState]:
        intscn_state_list = []
        for intscn_id, synced_tl_info_list in configs.items():
            if not self.__is_contain_abnormal(synced_tl_info_list):
                verticals, horizontals = self.__group_by_direction(synced_tl_info_list)
                intscn_state = self.__generate_state(verticals, horizontals)
                intscn_state.set_intscn_id(intscn_id)
                intscn_state_list.append(intscn_state)
                pass
            else:
                pass

        return intscn_state_list

    def __is_contain_abnormal(self, synced_tl_info_list: List[SyncedTLInfo]) -> bool:
        cnt_ped_only = 0
        for synced_tl_info in synced_tl_info_list:
            if synced_tl_info.abnormal_code.value == Abnormal.Pedestrian_only.value:
                cnt_ped_only += 1
        if cnt_ped_only == len(synced_tl_info_list):
            return True
        return False

    def __group_by_direction(self, synced_tl_info_list: SyncedTLInfo) -> Tuple[List[SyncedTLInfo], List[SyncedTLInfo]]:
        verticals = []
        horizontals = []
        for synced_tl_info in synced_tl_info_list:
            if synced_tl_info.direction.value == Direction.Vertical.value:
                verticals.append(synced_tl_info)
            elif synced_tl_info.direction.value == Direction.Horizontal.value:
                horizontals.append(synced_tl_info)

        return verticals, horizontals

    def __generate_state(self, verticals: List[SyncedTLInfo], horizontals: List[SyncedTLInfo]):
        num_synced_tl = (len(verticals) + len(horizontals))
        tl_state_list: List[SyncedTLState] = []

        if len(verticals) != 0:
            is_conflict_vertical = self.__is_turn_contact_point(verticals, self.__group_by_plane_vertical,
                                                                self.__get_most_outside_link_vertical_right,
                                                                self.__get_most_outside_link_vertical_left,
                                                                self.__compare_left_turn_vertical)
            if is_conflict_vertical:
                states = self.__define_conflict_left(verticals, num_synced_tl)
                for state in states:
                    tl_state_list.append(state)
            else:
                if self.__is_straight_contact_point(verticals):
                    states = self.__define_conflict_straight(verticals, num_synced_tl)
                    for state in states:
                        tl_state_list.append(state)
                else:
                    states = self.__define_straight(verticals, num_synced_tl)
                    for state in states:
                        if state.duration != 0:
                            tl_state_list.append(state)
                states = self.__define_left(verticals, num_synced_tl)
                for state in states:
                    if state.duration != 0:
                        tl_state_list.append(state)

                states = self.__define_ps_only(verticals, num_synced_tl)
                for state in states:
                    if state.duration != 0:
                        tl_state_list.append(state)

        if len(horizontals) != 0:
            is_conflict_horizontal = self.__is_turn_contact_point(horizontals, self.__group_by_plane_horizontal,
                                                                  self.__get_most_outside_link_horizontal_up,
                                                                  self.__get_most_outside_link_horizontal_down,
                                                                  self.__compare_left_turn_horizontal)
            if is_conflict_horizontal:
                states = self.__define_conflict_left(horizontals, num_synced_tl)
                for state in states:
                    tl_state_list.append(state)
            else:
                if self.__is_straight_contact_point(horizontals):
                    states = self.__define_conflict_straight(horizontals, num_synced_tl)
                    for state in states:
                        tl_state_list.append(state)
                else:
                    states = self.__define_straight(horizontals, num_synced_tl)
                    for state in states:
                        if state.duration != 0:
                            tl_state_list.append(state)
                states = self.__define_left(horizontals, num_synced_tl)
                for state in states:
                    if state.duration != 0:
                        tl_state_list.append(state)

                states = self.__define_ps_only(horizontals, num_synced_tl)
                for state in states:
                    if state.duration != 0:
                        tl_state_list.append(state)
        states = self.__define_straight_only(verticals, horizontals, tl_state_list, num_synced_tl)
        for state in states:
            if state.duration != 0:
                tl_state_list.append(state)

        tl_state = IntersectionState()
        tl_state.set_state(tl_state_list)
        return tl_state

    def __define_straight(self, direction_specific: List[SyncedTLInfo], num_synced_tl: int) -> List[SyncedTLState]:
        match_cnt = 0
        tl_bus = []
        states = []
        colors = ["R"] * num_synced_tl
        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                continue
            if 'straight' in synced_tl_info.colors:
                match_cnt += 1
        if match_cnt == 0:
            return [SyncedTLState().set_duration(0).set_lightcolor(colors)]

        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                continue
            if 'straight' in synced_tl_info.colors:
                colors[synced_tl_info.synced_tl_idx] = "SG"

        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                continue
            if 'straight' in synced_tl_info.colors and synced_tl_info.is_bus == True:
                tl_bus.append(synced_tl_info.synced_tl_idx)

        states.append(SyncedTLState().set_duration(40).set_lightcolor(colors).set_bus(tl_bus))

        return states

    def __define_conflict_straight(self, direction_specific: List[SyncedTLInfo], num_synced_tl: int) -> List[
        SyncedTLState]:
        states = []
        colors = ["R"] * num_synced_tl

        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                continue
            if 'straight' in synced_tl_info.colors:
                colors[synced_tl_info.synced_tl_idx] = "SG"
                states.append(SyncedTLState().set_duration(40).set_lightcolor(colors))
                colors = ["R"] * num_synced_tl

        return states

    def __define_left(self, direction_specific: List[SyncedTLInfo], num_synced_tl: int) -> SyncedTLState:
        match_cnt = 0
        tl_bus = []
        has_ps = False
        states = []
        colors = ["R"] * num_synced_tl
        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                continue
            if 'left' in synced_tl_info.colors or \
                    'left_unprotected' in synced_tl_info.colors:
                match_cnt += 1
        if match_cnt == 0:
            return [SyncedTLState().set_duration(0).set_lightcolor(colors)]

        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                continue
            if synced_tl_info.is_bus:
                tl_bus.append(synced_tl_info.synced_tl_idx)
            if 'left' in synced_tl_info.colors and synced_tl_info.colors.__len__() == 1 and synced_tl_info.has_pedestrian:
                colors[synced_tl_info.synced_tl_idx] = "G_with_GLeft"
                has_ps = True
                continue
            if 'left' in synced_tl_info.colors:
                colors[synced_tl_info.synced_tl_idx] = "R_with_GLeft"
            if 'left_unprotected' in synced_tl_info.colors:
                colors[synced_tl_info.synced_tl_idx] = "SG"

        states.append(SyncedTLState().set_duration(40).set_lightcolor(colors).set_bus(tl_bus).set_ps(has_ps))
        return states

    def __define_conflict_left(self, direction_specific: List[SyncedTLInfo], num_synced_tl: int) -> List[SyncedTLState]:
        states = []
        colors = ["R"] * num_synced_tl

        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                continue
            if 'left' in synced_tl_info.colors:
                colors[synced_tl_info.synced_tl_idx] = "G_with_GLeft"
                states.append(SyncedTLState().set_duration(40).set_lightcolor(colors))
                colors = ["R"] * num_synced_tl

        return states

    def __define_ps_only(self, direction_specific: List[SyncedTLInfo], num_synced_tl: int) -> List[SyncedTLState]:
        states = []
        colors = ["R"] * (num_synced_tl)

        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                colors[synced_tl_info.synced_tl_idx] = "Undefined"
        if "Undefined" not in colors:
            return [SyncedTLState().set_duration(0).set_lightcolor(colors)]

        states.append(SyncedTLState().set_duration(30).set_lightcolor(colors))
        return states

    def __define_straight_only(self, verticals: List[SyncedTLInfo], horizontals: List[SyncedTLInfo],
                               tl_state_list: List[SyncedTLState], num_synced_tl: int) -> List[SyncedTLState]:
        tl_bus = []
        states = []
        colors = ["R"] * num_synced_tl

        for state in tl_state_list:
            if "R_with_GLeft" in state.lightcolor or \
                    "G_with_GLeft" in state.lightcolor:
                return [SyncedTLState().set_duration(0).set_lightcolor(colors)]
            if "Undefined" in state.lightcolor:
                return [SyncedTLState().set_duration(0).set_lightcolor(colors)]

        for synced_tl_info in verticals + horizontals:
            if synced_tl_info.colors is None:
                continue
            if synced_tl_info.is_bus is True:
                tl_bus.append(synced_tl_info.synced_tl_idx)

        states.append(SyncedTLState().set_duration(30).set_lightcolor(colors).set_bus(tl_bus))
        return states

    def __is_turn_contact_point(self, direction_specific: List[SyncedTLInfo], grouping, get_outer_link, get_inner_link,
                                compare) -> bool:
        tls_left = []
        for synced_tl_info in direction_specific:
            if synced_tl_info.colors is None:
                continue
            if 'left' in synced_tl_info.colors:
                tls_left.append(synced_tl_info)

        if len(tls_left) == 0:
            return False
        positive_outer_link = None
        negative_outer_link = None
        positive_plane, negative_plane = grouping(tls_left)
        for synced_tl_info in positive_plane:
            positive_outer_link = get_outer_link(synced_tl_info)
        for synced_tl_info in negative_plane:
            negative_outer_link = get_inner_link(synced_tl_info)

        if positive_outer_link is None or negative_outer_link is None:
            return False

        result = compare(positive_outer_link, negative_outer_link)
        return result

    def __group_by_plane_vertical(self, direction_specific: List[SyncedTLInfo]) -> Tuple[
        List[SyncedTLInfo], List[SyncedTLInfo]]:
        left_plane = []
        right_plane = []
        for synced_tl_info in direction_specific:
            if synced_tl_info.plane.value == Plane.Left.value:
                left_plane.append(synced_tl_info)
            else:
                right_plane.append(synced_tl_info)

        return right_plane, left_plane

    def __group_by_plane_horizontal(self, direction_specific: List[SyncedTLInfo]) -> Tuple[
        List[SyncedTLInfo], List[SyncedTLInfo]]:
        up_plane = []
        down_plane = []
        for synced_tl_info in direction_specific:
            if synced_tl_info.plane.value == Plane.Up.value:
                up_plane.append(synced_tl_info)
            else:
                down_plane.append(synced_tl_info)

        return up_plane, down_plane

    def __get_most_outside_link_vertical_left(self, synced_tl_info: SyncedTLInfo) -> Link:
        min = numpy.Infinity
        from_node_idx = 0
        x_idx = 0
        if synced_tl_info.plane.value == Plane.Left.value:
            for idx, link in enumerate(synced_tl_info.link_list):
                if link.related_signal != 'left':
                    continue
                from_node_point_x = list(link.points[from_node_idx])[x_idx]
                if from_node_point_x < min:
                    min = from_node_point_x
                    min_idx = idx
            return synced_tl_info.link_list[min_idx]

    def __get_most_outside_link_vertical_right(self, synced_tl_info: SyncedTLInfo) -> Link:
        max_val = -numpy.Infinity
        from_node_idx = 0
        x_idx = 0
        if synced_tl_info.plane.value == Plane.Right.value:
            for idx, link in enumerate(synced_tl_info.link_list):
                if link.related_signal != 'left':
                    continue
                from_node_point_x = link.points[from_node_idx][x_idx]
                if from_node_point_x > max_val:
                    max_val = from_node_point_x
                    max_idx = idx
            return synced_tl_info.link_list[max_idx]

    def __get_most_outside_link_horizontal_up(self, synced_tl_info: SyncedTLInfo) -> Link:
        max = -numpy.Infinity
        from_node_idx = 0
        y_idx = 1
        if synced_tl_info.plane.value == Plane.Up.value:
            for idx, link in enumerate(synced_tl_info.link_list):
                if link.related_signal != 'left':
                    continue
                from_node_point_x = link.points[from_node_idx][y_idx]
                if from_node_point_x > max:
                    max = from_node_point_x
                    max_idx = idx
            return synced_tl_info.link_list[max_idx]

    def __get_most_outside_link_horizontal_down(self, synced_tl_info: SyncedTLInfo) -> Link:
        min_val = numpy.Infinity
        from_node_idx = 0
        y_idx = 1
        if synced_tl_info.plane.value == Plane.Down.value:
            for idx, link in enumerate(synced_tl_info.link_list):
                if link.related_signal != 'left':
                    continue
                from_node_point_x = link.points[from_node_idx][y_idx]
                if from_node_point_x < min_val:
                    min_val = from_node_point_x
                    min_idx = idx
            return synced_tl_info.link_list[min_idx]

    def __compare_left_turn_vertical(self, positive: Link, negative: Link) -> bool:
        mid_idx = math.floor(len(positive.points) / 2)
        px = positive.points[mid_idx][0]
        py = positive.points[mid_idx][1]
        mid_idx = math.floor(len(negative.points) / 2)
        nx = negative.points[mid_idx][0]
        ny = negative.points[mid_idx][1]
        if nx < px and ny < py:
            return True
        return False

    def __compare_left_turn_horizontal(self, positive: Link, negative: Link) -> bool:
        mid_idx = math.floor(len(positive.points) / 2)
        px = positive.points[mid_idx][0]
        py = positive.points[mid_idx][1]
        mid_idx = math.floor(len(negative.points) / 2)
        nx = negative.points[mid_idx][0]
        ny = negative.points[mid_idx][1]
        if nx > px and ny < py:
            return True
        return False

    def __is_straight_contact_point(self, direction_specific: List[SyncedTLInfo]) -> bool:
        is_conflict = self.__compare_straight_link_to_node(direction_specific)
        return is_conflict

    def __compare_straight_link_to_node(self, direction_specific) -> bool:
        to_nodes = []
        for synced_tl_info in direction_specific:
            for link in synced_tl_info.link_list:
                if link.to_node.idx not in to_nodes and link.related_signal == 'straight':
                    to_nodes.append(link.to_node.idx)
                elif link.related_signal == 'straight':
                    return True

        return False
