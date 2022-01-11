import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../../')))

import numpy as np
from class_defs.junction import Junction
from class_defs.junction_set import JunctionSet


def create_junction(junction_set, node_list):
    """node_list로부터 junction 인스턴스를 생성하고, junction_set에 추가한다.
    ---
    Return
        생성된 junction 인스턴스
    """
    junc_obj = Junction()
    for node in node_list:
        junc_obj.add_jc_node(node)

    junction_set.append_junction(junc_obj, create_new_key=True)
    return junc_obj


def delete_junction(junction_set, junction):
    """junction_set에서 junction 인스턴스를 삭제하고, junction 내부의 링크를 삭제한다
    Return
        삭제된 junction 인스턴스
    """
    # junction을 참조하고 있는 node에서, 이 junction에 대한 reference 제거
    for node in junction.jc_nodes:
        node.junctions.remove(junction)

    # junction 내 각 node에 대한 reference 제거
    junction.jc_nodes = []

    # junction_set에서 제거
    junction_set.junctions.pop(junction.idx)
    return junction


def edit_junction_id(junction_set, junction, new_id):
    if junction.idx not in junction_set.junctions.keys():
        raise BaseException('[ERROR] junction (id = {}) does not belong to the junction_set'.format(junction.idx))

    if new_id in junction_set.junctions.keys():
        raise BaseException('[ERROR] new_id = {} already exists in the junction_set'.format(new_id))

    # 현재 key를 삭제한다
    junction_set.junctions.pop(junction.idx)

    # 해당 object 내부의 id를 변경하고 새로운 key로 입력한다
    junction.idx = new_id
    junction_set.junctions[new_id] = junction


def edit_junction_node(junction, node_set, new_node_indices):
    """해당 junction을 구성하는 node를 새로운 node_indices로 표현되는 새로운 node들로 변경한다."""   
    # 에러 체크: new_node_indices 중에서 node_set에 존재하지 않는 값이 있는지 확인
    for node_id in new_node_indices:
        if node_id not in node_set.nodes.keys():
            raise BaseException('[ERROR] node_id = {} does not exist in the node_set.nodes'.format(node_id))

    # 삭제된 node_id 에 대해서는 reference를 끊어주고
    # 추가된 node_id 에 대해서는 새로 reference를 생성하면 된다

    prev_node_indices = junction.get_jc_node_indices()
          
    for prev_id in prev_node_indices:
        # 해당 junction에서 빠지는 node: 기존에 있던 id 인데 새로운 id 리스트에는 없는 것
        if prev_id not in new_node_indices:
            # reference를 node와 junction 양쪽에서 제거
            node = node_set.nodes[prev_id]
            node.junctions.remove(junction)
            junction.jc_nodes.remove(node)
    
    for new_id in new_node_indices:
        # 해당 junction에 새로 추가되는 node: 새로운 id인데 기존 id 리스트에는 없는 것
        if new_id not in prev_node_indices:
            # 새로운 reference를 생성한다 (아래 메소드를 통해 양쪽에서 reference를 한번에 생성)
            node = node_set.nodes[new_id]
            junction.add_jc_node(node)


    
