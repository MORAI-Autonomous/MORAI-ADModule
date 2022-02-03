import ast
import numpy as np

def delete_link(link_set, link):
    """선택한 링크를 삭제한다"""
    if link_set is None:
        raise BaseException('None is passed for an argument link_set')
   
    if link is None:
        raise BaseException('None is passed for an argument link')

    if link.included_plane:
        raise BaseException('This link has a plane associated to it\
            please delete the plane first')

    # 연결된 노드에서 line에 대한 reference를 제거한다
    to_node = link.get_to_node()
    from_node = link.get_from_node()

    to_node.remove_from_links(link)
    from_node.remove_to_links(link)

    # Line Set에서 line에 대한 reference를 제거한다
    link_set.remove_line(link)

    # 현재의 링크가 다른 링크의 dst link로 설정되어 있으면 이를 None으로 변경해주어야 한다
    for key, another_link in link_set.lines.items():
        
        # 차선 변경이 아닌 링크에 대해서만 검사하면 된다.
        if not another_link.is_it_for_lane_change():
            if another_link.get_left_lane_change_dst_link() is link:
                another_link.lane_ch_link_left = None
            if another_link.get_right_lane_change_dst_link() is link:
                another_link.lane_ch_link_right = None


def update_link(link_set, node_set, link, field_name, old_val, new_val):    
    if field_name == 'idx':
        if new_val in link_set:
            raise BaseException('The link (id = {}) already exists in the link list.'.format(new_val))

        setattr(link, field_name, new_val)
        link_set.pop(old_val)
        link_set[new_val] = link

    elif field_name == 'from_node':
        if new_val in node_set:
            node = node_set[new_val]
        elif new_val is None:
            node = None
        else:
            raise BaseException('The node (id = {}) is not included in the node list.'.format(new_val))  

        link.set_from_node(node)

    elif field_name == 'to_node':
        if new_val in node_set:
            node = node_set[new_val]
        elif new_val is None:
            node = None
        else:
            raise BaseException('The node (id = {}) is not included in the node list.'.format(new_val))   
        link.set_to_node(node)

    elif field_name == 'lane_ch_link_left':
        if new_val == 'None' or new_val is None:
            link.lane_ch_link_left = None
            return
        elif new_val not in link_set:
            raise BaseException('The link (id = {}) is not included in the link list.'.format(new_val))  
        
        ch_link = link_set[new_val]
        link.set_left_lane_change_dst_link(ch_link)

    elif field_name == 'lane_ch_link_right':
        if new_val == 'None' or new_val is None:
            link.lane_ch_link_right = None
            return
        elif new_val not in link_set:
            raise BaseException('The link (id = {}) is not included in the link list.'.format(new_val))

        ch_link = link_set[new_val]
        link.set_right_lane_change_dst_link(ch_link)

    elif field_name == 'points':
        point_array = np.array(new_val)
        setattr(link, field_name, point_array)

    elif field_name == 'force width (start)':
        setattr(link, 'force_width_start', new_val)
    
    elif field_name == 'force width (end)':
        setattr(link, 'force_width_end', new_val)

    else:
        setattr(link, field_name, new_val)