import ast
import numpy as np

def delete_node(node_set, node, delete_junction=False, junction_set=None):
    """node_set에서 node를 제거한다"""
    if node_set is None:
        raise BaseException('None is passed for an argument node_set')
    
    if node is None:
        raise BaseException('None is passed for an argument node')

    # 현재는 node가 dangling node일때만 삭제를 지원한다
    if not node.is_dangling_node():
        raise BaseException('Node must be a danling node to delete') 

    for jc in node.junctions:
        # junction에서 현재 노드에 대한 reference를 삭제한다
        jc.jc_nodes.remove(node)

        # junction에 남은 노드가 없으면 이번 노드를 삭제하면 junction도 삭제되어야 한다
        if delete_junction and len(jc.jc_nodes) == 0:
            if junction_set is None:
                raise BaseException('Error @ delete_node: junction_set must be provided to clear related junctions')
            junction_set.junctions.pop(jc.idx)
    node_set.remove_node(node)


def delete_nodes(node_set, delete_node_set):
    for node in delete_node_set:
        delete_node(node_set, node)


def update_node(node_set, link_set, junction_set, node, field_name, old_val, new_val):    
    if field_name == 'idx':
        if new_val in node_set:
            raise BaseException('The node (id = {}) already exists in the node list.'.format(new_val))

        setattr(node, field_name, new_val)
        node_set.pop(old_val)
        node_set[new_val] = node
    
    elif field_name == 'to_links':   
        old_val = ast.literal_eval(old_val)
        # 기존 to_links에 없던 새로운 link가 추가된 경우
        for link_id in new_val:
            if link_id not in old_val:
                # to_links 에 link 추가하고 Link의 from_node에도 해당 node 설정
                # 추가하려는 link에 이미 from_node가 있는 경우 Exeption 발생 
                if link_id in link_set:
                    link = link_set[link_id]
                else:
                    raise BaseException('The link (id = {}) is not included in the link list.'.format(link_id))               
                
                node.add_to_links(link)                
        
        # 기존 to_links에 있던 link가 삭제된 경우
        for link_id in old_val:
            if link_id not in new_val:
                if link_id in link_set:
                    link = link_set[link_id]
                else:
                    raise BaseException('The link (id = {}) is not included in the link list.'.format(link_id))               
                
                node.remove_to_links(link)

        # link id 리스트를 link 참조 리스트로 변환한 후 설정
        new_link_list = [] 
        for link_id in new_val:
            if link_id in link_set:
                    new_link_list.append(link_set[link_id])
            else:
                raise BaseException('The link (id = {}) is not included in the link list.'.format(link_id))               
              
        setattr(node, field_name, new_link_list)
    
    elif field_name == 'from_links':   
        old_val = ast.literal_eval(old_val)
        # 기존 to_links에 없던 새로운 link가 추가된 경우
        for link_id in new_val:
            if link_id not in old_val:
                # to_links 에 link 추가하고 Link의 from_node에도 해당 node 설정
                # 추가하려는 link에 이미 from_node가 있는 경우 Exeption 발생 
                if link_id in link_set:
                    link = link_set[link_id]
                else:
                    raise BaseException('The link (id = {}) is not included in the link list.'.format(link_id))               
                
                node.add_from_links(link)                
        
        # 기존 to_links에 있던 link가 삭제된 경우
        for link_id in old_val:
            if link_id not in new_val:
                if link_id in link_set:
                    link = link_set[link_id]
                else:
                    raise BaseException('The link (id = {}) is not included in the link list.'.format(link_id))               
                
                node.remove_from_links(link)

        # link id 리스트를 link 참조 리스트로 변환한 후 설정
        new_link_list = [] 
        for link_id in new_val:
            if link_id in link_set:
                    new_link_list.append(link_set[link_id])
            else:
                raise BaseException('The link (id = {}) is not included in the link list.'.format(link_id))               
              
        setattr(node, field_name, new_link_list)
    
    elif field_name == 'junctions':
        old_val = ast.literal_eval(old_val)
        # 기존 junctions에 없던 새로운 junction이 추가된 경우
        for junction_id in new_val:
            if junction_id not in old_val:                
                if junction_id in junction_set:
                    junction = junction_set[junction_id]
                else:
                    raise BaseException('The junction (id = {}) is not included in the junction list.'.format(junction_id))
                
                node.add_junction(junction)

        # 기존 junctions에 있던 junction이 삭제된 경우
        for junction_id in old_val:
            if junction_id not in new_val:
                if junction_id in junction_set:
                    junction = junction_set[junction_id]
                else:
                    raise BaseException('The junction (id = {}) is not included in the junction list.'.format(junction_id))
                
                node.remove_junctions(junction)

        # junctions id 리스트를 junctions 참조 리스트로 변환한 후 설정
        new_junction_list = [] 
        for junction_id in new_val:
            if junction_id in junction_set:
                    new_junction_list.append(junction_set[junction_id])
            else:
                raise BaseException('The link (id = {}) is not included in the link list.'.format(link_id))     
                
        setattr(node, field_name, new_junction_list)
        
    elif field_name == 'point':
        point_array = np.array(new_val)
        setattr(node, field_name, point_array)

    else:
        setattr(node, field_name, new_val)