import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../'))) # mgeo가 있는 경로를 추가한다.
sys.path.append(current_path + '/../../../lib/common/')
sys.path.append(current_path + '/../class_defs/')

from shp_common import *
from class_defs import *
from save_load import mgeo_load
from save_load import mgeo_save

import numpy as np
import matplotlib.pyplot as plt

def test_save():    
    input_path = '../../../../rsc/map_data/code42_shp_yangjae/'
    input_path = os.path.join(current_path, input_path)
    input_path = os.path.normpath(input_path)   

    output_path = '../../../../saved/'
    output_path = os.path.join(current_path, output_path)
    output_path = os.path.normpath(output_path)

    print('[INFO] input path:', input_path)
    print('[INFO] output path:', output_path) 
    
    # Get Map Information
    map_info = read_shp_files(input_path)

    """
    Origin이 되는 Point를 찾는다
    Origin은 현재는 A1_NODE에서 검색되는 첫번째 포인트로한다
    """
    origin = get_first_shp_point(map_info['yangjae_lane_node'])
    origin = np.array(origin)
    np.set_printoptions(suppress=True)
    print('[INFO] Origin =', origin)

    # 이제 여기서 NODE, LINK, SIGN, SIGNAL 파일을 읽어준다.
    shp_node = map_info['yangjae_lane_node']
    shp_link = map_info['yangjae_lane_link']
    shp_traffic_sign = map_info['yangjae_B1_SIGN_POINT']
    shp_traffic_light = map_info['yangjae_B1_SIGNAL_POINT']

    # Node, 일반 Link, 차선 변경 Link 생성하는 코드
    node_set_dict, junction_set = _create_node_set(shp_node, origin)
    line_set_dict = _create_line_set(shp_link, origin, node_set_dict)
    line_set_dict = set_all_left_right_links(line_set_dict)

    # Traffic Light, Traffic Sign 구성
    traffic_sign_set_dict = _create_traffic_sign_set(shp_traffic_sign, origin, line_set_dict)
    traffic_light_set_dict = _create_traffic_light_set(shp_traffic_light, origin, line_set_dict)

    # 파일 저장
    MGeoPlannerMap.save_signal(output_path, traffic_sign_set_dict, traffic_light_set_dict)

    print('[INFO] Ended Successfully.')
    
def test_load():
    output_path = '../../../../saved/'
    output_path = os.path.join(current_path, output_path)
    output_path = os.path.normpath(output_path)

    sign_set, light_set = MGeoPlannerMap.load_signal(output_path)

def _create_traffic_sign_set(sf, origin, link_set):   
    traffic_sign_set = SignalSet()

    shapes = sf.shapes()
    records  = sf.records()

    if len(shapes) != len(records):
        raise BaseException('[ERROR] len(shapes) != len(records)')
    
    for i in range(len(shapes)):
        shp_rec = shapes[i]
        dbf_rec = records[i]

        # Convert to numpy array
        shp_rec.points = np.array(shp_rec.points)
        shp_rec.z = np.array(shp_rec.z)

        # Point에 z축 값도 그냥 붙여버리자
        shp_rec.points = np.c_[shp_rec.points, shp_rec.z]

        # origin 무조건 전달, 상대좌표로 변경
        shp_rec.points -= origin

        traffic_sign = Signal(dbf_rec['HDUFID'])

        traffic_sign.link_id = dbf_rec['LINKID'] 
        traffic_sign.dynamic = False
        traffic_sign.orientation = '+'
        traffic_sign.country = 'KR'

        # LINK ID가 없는 경우 존재
        if traffic_sign.link_id in link_set.lines:
            traffic_sign.link = link_set.lines[traffic_sign.link_id]
    
        traffic_sign.type = dbf_rec['CODE']
        traffic_sign.sub_type = dbf_rec['SIGNTYPE']

        # 사이즈 설정
        # type, sub_type 값을 설정한 후 호출해야 함
        traffic_sign.set_size()

        # 최고속도제한 규제표지
        if traffic_sign.type == 2 and traffic_sign.sub_type == 224 and traffic_sign.link != None :
            traffic_sign.value = traffic_sign.link.max_speed_kph
        # 최저속도제한 규제표지
        elif traffic_sign.type == 2 and traffic_sign.sub_type == 225 and traffic_sign.link != None :
            traffic_sign.value = traffic_sign.link.min_speed_kph
             
        traffic_sign.point = shp_rec.points[0]
        
        traffic_sign_set.signals[traffic_sign.idx] = traffic_sign
       
    return traffic_sign_set

def _create_traffic_light_set(sf, origin, link_set):
    traffic_light_set = SignalSet()

    shapes = sf.shapes()
    records  = sf.records()

    if len(shapes) != len(records) :
        raise BaseException('[ERROR] len(shapes) != len(records)')
    
    for i in range(len(shapes)):
        shp_rec = shapes[i]
        dbf_rec = records[i]

        # Convert to numpy array
        shp_rec.points = np.array(shp_rec.points)
        shp_rec.z = np.array(shp_rec.z)

        # Point에 z축 값도 그냥 붙여버리자
        shp_rec.points = np.c_[shp_rec.points, shp_rec.z]

        # origin 무조건 전달, 상대좌표로 변경
        shp_rec.points -= origin

        traffic_light = Signal(dbf_rec['HDUFID'])
        traffic_light.link_id = dbf_rec['LINKID']
        traffic_light.dynamic = True
        traffic_light.orientation = '+'
        traffic_light.country = 'KR'

        # LINK ID가 없는 경우 존재
        if traffic_light.link_id in link_set.lines :
            traffic_light.link = link_set.lines[traffic_sign.link_id]

        traffic_light.type = dbf_rec['CODE']
        traffic_light.sub_type = dbf_rec['SIGNTYPE']

        # 사이즈 설정
        # type, sub_type 값을 설정한 후 호출해야 함
        traffic_light.set_size()

        traffic_light.point = shp_rec.points[0]
        
        traffic_light_set.signals[traffic_light.idx] = traffic_light
       
    return traffic_light_set

def _create_node_set(sf, origin):
    node_set = NodeSet()
    junction_set = JunctionSet()
    
    shapes = sf.shapes()
    records  = sf.records()
    fields = sf.fields

    if len(shapes) != len(records):
        raise BaseException('[ERROR] len(shapes) != len(records)')
    
    for i in range(len(shapes)):
        shp_rec = shapes[i]
        dbf_rec = records[i]

        # Convert to numpy array
        shp_rec.points = np.array(shp_rec.points)
        shp_rec.z = np.array(shp_rec.z)

        # Point에 z축 값도 그냥 붙여버리자
        shp_rec.points = np.c_[shp_rec.points, shp_rec.z]

        # origin 무조건 전달, 상대좌표로 변경
        shp_rec.points -= origin

        # node로 추가
        node = Node(dbf_rec['nodeId'])
        node.point = shp_rec.points[0]

        # node를 node_set에 포함
        node_set.nodes[node.idx] = node

    return node_set, junction_set


def _create_line_set(sf, origin, node_set):
    line_set = LineSet()

    shapes = sf.shapes()
    records  = sf.records()
    fields = sf.fields

    if len(shapes) != len(records):
        raise BaseException('[ERROR] len(shapes) != len(records)')

    for i in range(len(shapes)):
        shp_rec = shapes[i]
        dbf_rec = records[i]

        # Convert to numpy array
        shp_rec.points = np.array(shp_rec.points)
        shp_rec.z = np.array(shp_rec.z)

        # Point에 z축 값도 그냥 붙여버리자
        shp_rec.points = np.c_[shp_rec.points, shp_rec.z]

        # origin 무조건 전달, 상대좌표로 변경
        shp_rec.points -= origin

        # 현재는 전부 바로 point가 init되는 Link를 생성
        link = Link(points=shp_rec.points, idx=dbf_rec['laneId'], lazy_point_init=False)
    
        from_node = node_set.nodes[dbf_rec['fromNode']]
        to_node = node_set.nodes[dbf_rec['toNode']]

        link.road_id = dbf_rec['roadId']
        link.ego_lane = dbf_rec['egoLane']

        if dbf_rec['hov'] == 1:
            link.hov = True
        else:
            link.hov = False

        # 양옆 차선 속성도 dbf 데이터로부터 획득
        link.lane_change_dir = dbf_rec['laneChange']

        link.set_from_node(from_node)
        link.set_to_node(to_node)
        line_set.lines[link.idx] = link

    return line_set


def _create_lane_change_line_set(sf, line_set):
    lane_ch_line_set = LineSet()
    
    shapes = sf.shapes()
    records  = sf.records()
    fields = sf.fields

    if len(shapes) != len(records):
        raise BaseException('[ERROR] len(shapes) != len(records)')

    for i in range(len(shapes)):
        dbf_rec = records[i]
        src_line = line_set.lines[dbf_rec['ID']]
        
        if dbf_rec['LinkType'] in ['1', '2', '3']:
            continue

        if dbf_rec['L_LinKID'] != '':
            dst_line = line_set.lines[dbf_rec['L_LinKID']]

            # TODO(sglee): code42의 geojson 작업 시 수행했던 것과 같이, R_LinkID, L_LinkID가 pair인지 확인

            to_node = dst_line.get_to_node()
            from_node = src_line.get_from_node()

            idx = src_line.idx + '-' + dbf_rec['L_LinKID'] 
            lane_ch_line = Link(idx=idx, lazy_point_init=True)
            lane_ch_line.set_points_using_node_lazy_init(from_node, to_node)
            
            # 어느 링크에서 어느 링크로 가는지 표현
            lane_ch_line.set_lane_change_from_link(src_line)
            lane_ch_line.set_lane_change_to_link(dst_line)
            
            # 새로 만드는 set에 추가
            lane_ch_line_set.lines[lane_ch_line.idx] = lane_ch_line

        
        if dbf_rec['R_LinkID'] != '':
            dst_line = line_set.lines[dbf_rec['R_LinkID']]

            # TODO(sglee): code42의 geojson 작업 시 수행했던 것과 같이, R_LinkID, L_LinkID가 pair인지 확인

            to_node = dst_line.get_to_node()
            from_node = src_line.get_from_node()

            idx = src_line.idx + '-' + dbf_rec['R_LinkID'] 
            lane_ch_line = Link(idx=idx, lazy_point_init=True)
            lane_ch_line.set_points_using_node_lazy_init(from_node, to_node)

            # 어느 링크에서 어느 링크로 가는지 표현
            lane_ch_line.set_lane_change_from_link(src_line)
            lane_ch_line.set_lane_change_to_link(dst_line)

            # 새로 만드는 set에 추가
            lane_ch_line_set.lines[lane_ch_line.idx] = lane_ch_line

    return lane_ch_line_set


def set_all_left_right_links(link_set):
    '''
    author: HJP
    Link 객체의 좌/우 접한 차선 정보를 저장 가능한 self.lane_ch_link_left(or right)
    self.lane_ch_link_left(or right) 변수에 할당할 Link를 검색 후 저장
    '''
    for select_link in link_set.lines.values():

        selected_link_road = select_link.road_id
        selected_link_ego = select_link.ego_lane
        lane_left = select_link.lane_ch_link_left
        lane_right = select_link.lane_ch_link_right

        matched_list = list()
        
        # check lane id format for select_link
        lane_id = str(select_link.idx)
        init_lane = lane_id[(len(lane_id)-3):len(lane_id)]
        init_lane = int(init_lane)
        init_lane = init_lane - (init_lane % 100)
        # NOTE: Designed to be foolproof, provided that the source data has properly
        # sequenced lane IDs (i.e. no omitted series like [101, 102, 104, 105])
        # and sequential egolane ids

        result = 0

        while result is not None:
            init_lane += 1
            leading_zero_id = '0{}'.format(init_lane)
            concat_lane_id = str(selected_link_road) + leading_zero_id
            search_lane_id = int(concat_lane_id)
            result = link_set.lines.get(search_lane_id)
            if result is not None:
                matched_list.append(result)

        for matched_lane in matched_list:
            if matched_lane.ego_lane == selected_link_ego - 1:
                select_link.set_left_lane_change_dst_link(matched_lane)
            elif matched_lane.ego_lane == selected_link_ego + 1:
                select_link.set_right_lane_change_dst_link(matched_lane)

    return link_set

if __name__ == u'__main__':
    #test_save()
    test_load()