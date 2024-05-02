import json
import math

ONE_DEGREE = 111.321 # [km]
WALK_SPEED = 4 # [km/h]
DRIVE_SPEED = 34 # [km/h]
# パラメータ 小さい < --------------------------------> 大きい
# ランキング上位を選択 <--------------------> 距離が近い方を選択
# y = moving_itme * (rank + parameter)
PARAMETER = [-1, -0.1, 0, 0.1, 1] 

def get_longitude_latitude_from_table(response):
    """
    return {id: [longitude, latitude, rank, staying_time], ...}
    """

    item_dic = {}
    for item in response.data:
        id = item["id"]
        longitude = item["longitude"]
        latitude = item["latitude"]
        rank = item["rank"]
        staying_time = item["staying_time"]
        item_dic[id] =  [longitude, latitude, rank, staying_time]
    return item_dic

def calc_weight(location1, location2, rank, parameter):
    moving_time = calc_moving_time(location1, location2)
    weight = moving_time * (rank + parameter)
    return weight

def calc_moving_time(location1, location2):
    distance = math.sqrt((location1[0]-location2[0])**2 + (location1[1]-location2[1])**2)
    moving_time = (distance * ONE_DEGREE) / WALK_SPEED
    return moving_time

def greedy(locations):
    """
    return order list 
    """
    N = len(locations)
    moving_time = [[0] * N for i in range(N)]
    weight = [[0] * N for i in range(N)]

    for i in range(N):
        for j in range(N):
            moving_time[i][j] = moving_time[j][i] = calc_moving_time(locations[i+1],locations[j+1])
            weight[i][j] = calc_weight(locations[i+1],locations[j+1], rank=locations[j+1][2], parameter=PARAMETER[0])
            weight[j][i] = calc_weight(locations[i+1],locations[j+1], rank=locations[i+1][2], parameter=PARAMETER[0])

    min_sum_time_including_weight = float('inf')
    best_root = []
    for i in range(N):
        tmp_sum_time_including_weight = 0
        total_time = 0
        current_location = i
        unvisited_locations = set(range(N))
        unvisited_locations.remove(i)

        root = [current_location]
        while unvisited_locations:
            next_location = min(unvisited_locations, key=lambda location: weight[current_location][location])
            unvisited_locations.remove(next_location)
            root.append(next_location)
            tmp_sum_time_including_weight += weight[current_location][next_location]
            staying_time = locations[next_location+1][3]
            total_time += calc_moving_time(locations[current_location+1], locations[next_location+1]) + staying_time
            current_location = next_location
        
        if tmp_sum_time_including_weight < min_sum_time_including_weight:
            best_root = root
            min_sum_time_including_weight = tmp_sum_time_including_weight

    return best_root

def make_json_for_root(best_root):
    """
    return {"root": [{"id": i, "order": j} ..... ]}
    """
    root_list = []
    for i in range(len(best_root)):
        json_order = {"id": best_root[i]+1, "order": i+1}
        root_list.append(json_order)
    
    with open("root.json","w") as file:
        json.dump({"root": root_list}, file)
    return {"root": root_list}

def make_root(response):
    best_root_list = greedy(get_longitude_latitude_from_table(response))
    return make_json_for_root(best_root_list)