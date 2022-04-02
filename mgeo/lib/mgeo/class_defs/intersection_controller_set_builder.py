#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

from class_defs.line_set import LineSet
from lib.mgeo.class_defs.intersection_controller import IntersectionController
from lib.mgeo.class_defs.intersection_controller_set import IntersectionControllerSet
from lib.mgeo.class_defs.synced_signal_set import SyncedSignalSet

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

from class_defs.signal import Signal
from class_defs.signal_set import SignalSet
from class_defs.synced_signal import SyncedSignal

import math

from collections import defaultdict

from typing import DefaultDict, List, Tuple


class IntersectionInfo(object):
    def __init__(self) -> None:
        self.tl_dict: DefaultDict[str, Signal] = defaultdict(Signal)
        self.link_tl_mapping: DefaultDict[str, List[str]] = defaultdict(list)
        self.tl_intscn_set: DefaultDict[str, List[List[str]]] = defaultdict(list)


class IntersectionControllerSetBuilder(object):
    def __init__(self, light_set: SignalSet, line_set: LineSet, struct: IntersectionInfo):
        self.from_node_link_mapping: DefaultDict[str, List[str]] = defaultdict(list)
        self.intscn_set: List[List[str]] = []
        self.tl_dict: DefaultDict[str, Signal] = struct.tl_dict
        self.link_tl_mapping: DefaultDict[str, List[str]] = struct.link_tl_mapping
        self.tl_intscn_set: DefaultDict[str, List[List[str]]] = struct.tl_intscn_set
        self.synced_signal_set: List[SyncedSignal] = []
        self.intscn_ctrlr_set: List[IntersectionController] = []
        self.__build(light_set, line_set)

    def build_synced_signal_set(self, mgeo_synced_sig_set: SyncedSignalSet):
        for synced_signal_list in self.synced_signal_set:
            for synced_signal in synced_signal_list:
                mgeo_synced_sig_set.append_synced_signal(synced_signal)

    def build_controller(self, mgeo_intscn_controller: IntersectionControllerSet):
        for controller in self.intscn_ctrlr_set:
            mgeo_intscn_controller.append_controller(controller)

    def __build(self, light_set: SignalSet, line_set: LineSet):
        self.__set_light_set_internal(light_set, line_set)
        self.__find_intscn_internal(line_set)
        self.__find_synced_traffic_light_internal()
        self.__to_mgeo_data_internal()

    def __set_light_set_internal(self, light_set: SignalSet, line_set: LineSet):
        for tl_id, tl in light_set.signals.items():
            self.tl_dict[tl_id] = tl
            for link_id in tl.link_id_list:
                self.link_tl_mapping[link_id].append(tl_id)
                if line_set.lines[link_id] not in tl.link_list:
                    tl.link_list.append(line_set.lines[link_id])

    def __find_intscn_internal(self, link_set: LineSet) -> None:
        node_graph, node_position = self.__make_graph(link_set)
        intersection_list = []
        intersection_nodes = []
        for start_node in self.from_node_link_mapping.keys():
            if start_node not in intersection_nodes:
                intersection_nodes = sorted(self.__depth_first_search(node_graph, start_node))
                if intersection_nodes not in intersection_list:
                    intersection_list.append(intersection_nodes)
        intra_cluster_distances = defaultdict(float)
        inter_cluster_distances = defaultdict(float)
        for idx, intscn in enumerate(intersection_list):
            intra_cluster_distances["h" + str(idx)] = self.__get_intra_cluster_distance(intscn, node_position)
        inter_cluster_distances = self.__get_inter_cluster_distance(intersection_list, node_position)
        union_candidates = self.__find_union(intra_cluster_distances, inter_cluster_distances)
        self.intscn_set = self.__make_union(intersection_list, union_candidates)
        self.intscn_set = self.__delete_subset(self.intscn_set)

    def __make_graph(self, link_set: LineSet) -> Tuple[DefaultDict[str, List[str]], DefaultDict[str, List[str]]]:
        links_tl_list = [link for link in self.link_tl_mapping.keys()]
        node_graph = defaultdict(list)
        node_position = defaultdict(list)
        visited = []
        for line_idx, line in link_set.lines.items():
            if line_idx in links_tl_list:
                node_graph[line.from_node.idx].append(line.to_node.idx)
                node_graph[line.from_node.idx].sort()
                node_graph[line.to_node.idx].append(line.from_node.idx)
                node_graph[line.to_node.idx].sort()
                if line.from_node.idx not in visited:
                    visited.append(line.from_node.idx)
                    node_position[line.from_node.idx].extend(list(line.points[0]))
                if line.to_node.idx not in visited:
                    visited.append(line.to_node.idx)
                    node_position[line.to_node.idx].extend(list(line.points[-1]))
                self.from_node_link_mapping[line.from_node.idx].append(line_idx)
        return node_graph, node_position

    def __depth_first_search(self, graph: DefaultDict[str, List[str]], start_node: str) -> List[str]:
        visited = []
        stack = [start_node]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.append(node)
                stack.extend(graph[node])
        return visited

    def __get_intra_cluster_distance(self, intscn_nodes: List[str], positions: DefaultDict[str, List[float]]) -> float:
        distance = []
        head_node = self.__make_head_node(intscn_nodes, positions)
        for node in intscn_nodes:
            l2_norm = math.sqrt(math.pow(positions[node][0] - head_node[0], 2) +
                                math.pow(positions[node][1] - head_node[1], 2) +
                                math.pow(positions[node][2] - head_node[2], 2))
            distance.append(l2_norm)
        return max(distance)

    def __get_inter_cluster_distance(self, intscn_list: List[List[str]], positions: DefaultDict[str, List[float]]) -> \
    DefaultDict[Tuple[str, str], float]:
        from itertools import combinations
        heads = defaultdict(list)
        distance = defaultdict(float)
        for idx, intscn in enumerate(intscn_list):
            # heads["h"+str(idx)].extend(self.__make_head_node(intscn, positions))
            heads[idx].extend(self.__make_head_node(intscn, positions))
        for p1, p2 in combinations(heads, 2):
            l2_norm = math.sqrt(math.pow(heads[p1][0] - heads[p2][0], 2) +
                                math.pow(heads[p1][1] - heads[p2][1], 2) +
                                math.pow(heads[p1][2] - heads[p2][2], 2))
            distance[(p1, p2)] = l2_norm
        return distance

    def __make_head_node(self, intscn_nodes: List[str], positions: DefaultDict[str, List[float]]) -> List[float]:
        px, py, pz = [], [], []
        for node in intscn_nodes:
            px.append(positions[node][0])
            py.append(positions[node][1])
            pz.append(positions[node][2])
        return [sum(px) / len(px), sum(py) / len(py), sum(pz) / len(pz)]

    def __find_union(self, intra_dist: DefaultDict[str, float], inter_dist: DefaultDict[Tuple[str, str], float]) -> \
    List[List[str]]:
        unions = defaultdict(list)
        head_pair = [list(keys) for keys in list(inter_dist.keys())]
        max_distance = max(intra_dist.values())
        for cluster_1, cluster_2 in head_pair:
            if inter_dist[tuple([cluster_1, cluster_2])] <= 1.5 * max_distance:
                # if (inter_dist[tuple([cluster_1, cluster_2])] <= max_distance):
                unions[cluster_1].append(cluster_2)
        return unions

    def __make_union(self, intscn_list: List[List[str]], cluster_heads: DefaultDict[str, List[str]]) -> List[List[str]]:
        visited = []
        intersections = []
        for head_1, heads in cluster_heads.items():
            intersection = []
            if head_1 not in visited:
                visited.append(head_1)
                visited.extend(heads)
                intersection.extend(intscn_list[head_1])
                for head in heads:
                    intersection.extend(intscn_list[head])
                intersection = list(set(intersection))
                intersection.sort()
                intersections.append(intersection)
        return intersections

    def __delete_subset(self, intscn_set: List[List[str]]):
        intscn_list = []
        deleted = []
        for i in range(len(intscn_set)):
            for j in range(len(intscn_set)):
                if i == j:
                    continue

                if set(intscn_set[i]).issuperset(set(intscn_set[j])):
                    deleted.append(j)
                if set(intscn_set[i]).issubset(set(intscn_set[j])):
                    deleted.append(i)

        deleted = list(set(deleted))
        if len(deleted) == 0:
            return intscn_set

        for i in range(len(intscn_set)):
            if i not in deleted:
                intscn_list.append(intscn_set[i])
        return intscn_list

    def __find_synced_traffic_light_internal(self) -> None:
        intscn_link_set = self.__find_intscn_link_set()
        for idx, link_list in enumerate(intscn_link_set):
            for link in link_list:
                if self.link_tl_mapping[link] not in self.tl_intscn_set[idx]:
                    self.tl_intscn_set[idx].append(sorted(self.link_tl_mapping[link]))
        for key in self.tl_intscn_set.keys():
            self.tl_intscn_set[key] = sorted(self.tl_intscn_set[key], key=lambda li: li[0])
        self.__make_intscn_synced_tl_unique()
        self.__delete_tl_subset()

    def __find_intscn_link_set(self) -> List[List[str]]:
        intscn_links = []
        link_list = []
        for intscn in self.intscn_set:
            for node in intscn:
                if node in self.from_node_link_mapping:
                    link_list.extend(self.from_node_link_mapping[node])
            link_set = set(link_list)
            intscn_links.append(sorted(list(link_set)))
            link_list.clear()
        return intscn_links

    def __make_intscn_synced_tl_unique(self):
        for key in self.tl_intscn_set.keys():
            unique_synced_tl = set(list(map(tuple, self.tl_intscn_set[key])))
            unique_synced_tl = sorted(unique_synced_tl, key=lambda li: li[0])
            unique_synced_tl = self.__delete_subset(unique_synced_tl)
            self.tl_intscn_set[key] = list(map(list, unique_synced_tl))

    def __delete_tl_subset(self):
        deleted = []
        for i in range(len(self.tl_intscn_set)):
            for j in range(i, len(self.tl_intscn_set)):
                if i == j:
                    continue
                if self.tl_intscn_set[i] == self.tl_intscn_set[j]:
                    deleted.append(i)
                    continue
                if set(list(map(tuple, self.tl_intscn_set[i]))).issubset(set(list(map(tuple, self.tl_intscn_set[j])))):
                    deleted.append(i)
                if set(list(map(tuple, self.tl_intscn_set[j]))).issubset(set(list(map(tuple, self.tl_intscn_set[i])))):
                    deleted.append(j)

        deleted = list(set(deleted))
        for idx in reversed(deleted):
            del self.tl_intscn_set[idx]

    def __to_mgeo_data_internal(self):
        for idx, intscn_tl_list in self.tl_intscn_set.items():
            self.synced_signal_set.append(self.__make_synced_signal_set(idx, intscn_tl_list))
            self.intscn_ctrlr_set.append(self.__make_intersection_controller(idx, intscn_tl_list))

    def __make_synced_signal_set(self, intscn_idx: int, intscn_tl_list: List[List[str]]) -> SyncedSignal:
        import numpy
        synced_signal_list = []
        for synced_idx, synced_tl in enumerate(intscn_tl_list):
            synced_signal = SyncedSignal(f'SSN{intscn_idx:03}{synced_idx:03}')
            synced_signal.intersection_controller_id = f'IntTL{intscn_idx:03}'
            signal_set = SignalSet()
            points = DefaultDict(list)
            for tl in synced_tl:
                tl_obj = self.tl_dict[tl]
                points[tl].extend(list(tl_obj.point))
                signal_set.append_signal(tl_obj)
            # center_of_synced_signal = self.__make_head_node(synced_tl, points)
            # synced_signal.point = numpy.array(center_of_synced_signal)
            synced_signal.point = numpy.array(list(points.values()))
            synced_signal.link_id_list.extend(link for tl in synced_tl for link in self.tl_dict[tl].link_id_list)
            synced_signal.signal_id_list.extend(synced_tl)
            synced_signal.signal_set = signal_set
            synced_signal_list.append(synced_signal)
        return synced_signal_list

    def __make_intersection_controller(self, intscn_idx: int,
                                       intscn_tl_list: List[List[str]]) -> IntersectionController:
        intscn_tl_controller = IntersectionController(f'IntTL{intscn_idx:03}')
        for intscn_tl in intscn_tl_list:
            intscn_tl_controller.new_synced_signal()
            for tl in intscn_tl:
                tl_obj = self.tl_dict[tl]
                intscn_tl_controller.append_signal(tl_obj)
        return intscn_tl_controller
