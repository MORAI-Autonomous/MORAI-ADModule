import ast
import numpy as np

def delete_lane(lane_set, lane):
    """선택한 링크를 삭제한다"""
    if lane_set is None:
        raise BaseException('None is passed for an argument link_set')
   
    if lane is None:
        raise BaseException('None is passed for an argument link')

    # 연결된 노드에서 line에 대한 reference를 제거한다
    to_node = lane.get_to_node()
    from_node = lane.get_from_node()

    to_node.remove_from_links(lane)
    from_node.remove_to_links(lane)

    # Line Set에서 line에 대한 reference를 제거한다
    lane_set.remove_line(lane)

def update_lane(lane_set, node_set, lane, field_name, old_val, new_val):    
    if field_name == 'idx':
        if new_val in lane_set:
            raise BaseException('The lane (id = {}) already exists in the lane list.'.format(new_val))

        setattr(lane, field_name, new_val)
        lane_set.pop(old_val)
        lane_set[new_val] = lane

    elif field_name == 'points':
        point_array = np.array(new_val)
        setattr(lane, field_name, point_array)

    elif field_name == 'lane_shape':
        new_val = ast.literal_eval(new_val)
        setattr(lane, field_name, new_val)
    
    else:
        setattr(lane, field_name, new_val)