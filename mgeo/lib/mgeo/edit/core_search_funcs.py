import numpy as np
      

def find_nearest_point_node_base(node_set, search_coord):
    if node_set is None:
        print_warn('[ERROR] There is no node_set')
        return

    min_dist = np.inf
    nearest_node = None
    for idx in node_set.nodes:
        node = node_set.nodes[idx]

        if node.point[0:2].shape != (2,) :
            raise BaseException('[ERROR] @ _find_nearest_point_node_base: node.point.shape is not what is expected.')

        pos_vector = node.point[0:2] - search_coord
        dist = np.linalg.norm(pos_vector, ord=2)
        if dist < min_dist and dist > 0:
            min_dist = dist
            nearest_node = node

    return min_dist, nearest_node


def find_nearest_point_node_auto(node_set, search_node, search_node_links):
    if node_set is None:
        print_warn('[ERROR] There is no node_set')
        return

    min_dist = np.inf
    nearest_node = None
    for idx in node_set.nodes:
        node = node_set.nodes[idx]

        # 거리 계산할 node들이 점검조건을 만족하는지 확인
        # (search_node는 이미 윗단에서 수행)
        node_links = node.get_to_links() + node.get_from_links()
        if (len(node_links) > 1
            or node in self.eliminated_list
            or node_links[0] is search_node_links[0]):
            continue

        if node.point[0:2].shape != (2,):
            raise BaseException('[ERROR] @ _find_nearest_point_node_base: node.point.shape is not what is expected.')

        pos_vector = node.point[0:2] - search_node.point[0:2]
        dist = np.linalg.norm(pos_vector, ord=2)
        if dist < min_dist and dist > 0:
            min_dist = dist
            nearest_node = node

    return min_dist, nearest_node


def find_nearest_point_ref_point_base(self, search_coord):
    if self.ref_points is None:
        print_warn('[ERROR] ref_points must be initialized using set_geometry_obj method')
        return

    # search for nearest node coordinates
    closest_dist = np.inf
    point_found = False
    dist_click = np.sqrt(search_coord[0]**2 + search_coord[1]**2)
    
    for i in range(len(self.ref_points)):
        # 현재 선택된 포인트는 다시 선택하지 않도록 Skip한다
        if self.current_selected_point_idx_in_ref_point != None:
            if i == self.current_selected_point_idx_in_ref_point:
                print('[DEBUG] Skipping currently selected point ({})'.format(i))
                continue

        x_diff = self.ref_points[i]['coord'][0] - search_coord[0]
        y_diff = self.ref_points[i]['coord'][1] - search_coord[1]
        dist_candidate = np.sqrt(x_diff**2 + y_diff**2)

        if dist_candidate < closest_dist:
            closest_dist = dist_candidate
            selected_point = self.ref_points[i]
            selected_point_idx_in_ref_point = i
            point_found = True

    if point_found is False:
        print_warn('[ERROR] Reference point not found! Try clicking away from\
            the graphs\'s origin')
        return

    # 반드시 리턴하기 전에 별도로 저장해주어야 한다
    # For loop 내에서 이를 업데이트하면 정상적으로 동작할 수 없다
    self.current_selected_point_idx_in_ref_point = selected_point_idx_in_ref_point
    return closest_dist, selected_point