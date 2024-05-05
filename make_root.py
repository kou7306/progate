from supabase import create_client, Client
import itertools
import json
import math

ONE_DEGREE = 111.321 # [km]
WALK_SPEED = 4 # [km/h]
DRIVE_SPEED = 34 # [km/h]

with open('key.json') as f:
    key_data = json.load(f)

url: str = key_data['supabase_url']
key: str = key_data['supabase_key']
supabase: Client = create_client(url, key)
response = supabase.table('address').select("*").execute()

def create_item_dict(rank_list: list, main_place_list: list) -> dict:
    """
    return {rank: [id, longitude, latitude, staying_time, place_name], ...}
    """

    # main_placeのランクを0とする
    item_dict = {0: [-1, main_place_list[0], main_place_list[1], main_place_list[2], main_place_list[3]]}
    rank = 1

    for item in response.data:
        id = item["id"]
     
        if id in rank_list:
            longitude = item["longitude"]
            latitude = item["latitude"]
            staying_time = item["staying_time"]
            place_name = item["place_name"]
            item_dict[rank] =  [id, longitude, latitude, staying_time, place_name]
            rank += 1
    
    return item_dict

def calc_moving_time(rank1: list, rank2: list, drive: bool) -> float:
    distance = math.sqrt((rank1[1]-rank2[1])**2 + (rank1[2]-rank2[2])**2)
    speed = DRIVE_SPEED if drive else WALK_SPEED
    moving_time = (distance * ONE_DEGREE) * 1.5 / speed
    return moving_time

def make_moving_time_list(item_dict: dict, drive: bool) -> list:
    N = len(item_dict)
    moving_time = [[0] * N for i in range(N)]

    for i in range(N):
        for j in range(N):
            moving_time[i][j] = moving_time[j][i] = calc_moving_time(item_dict[i], item_dict[j], drive)
    return moving_time

def greedy(item_dict: dict, rank_list: list, moving_time: list, limit_time: float) -> list:
    """
    return order list of rank
    ex: [2,1,5...] の時は、rank=2,1,5の順に回る
    """

    min_sum_time = limit_time
    best_root = []
    
    for rank in rank_list:
        current_rank = rank
        tmp_sum_time = item_dict[current_rank][3]
        unvisited_ranks = set(rank_list)
        unvisited_ranks.remove(rank)

        root = [current_rank]
        while unvisited_ranks:
            next_rank = min(unvisited_ranks, key=lambda rank: moving_time[current_rank-1][rank-1])
            unvisited_ranks.remove(next_rank)
            root.append(next_rank)
            staying_time = item_dict[next_rank][3]
            tmp_sum_time += moving_time[current_rank-1][next_rank-1] + staying_time
            current_rank = next_rank

        if tmp_sum_time < min_sum_time:
            best_root = root
            min_sum_time = tmp_sum_time
        
    return best_root

def try_all_combinations(item_dict: dict, id_list: list, moving_time:list, limit_time: bool) -> list:
    best_root = []
    max_rank_point = 0
    for i in range(1, len(id_list)+1):
        for combination in itertools.combinations(enumerate(id_list),i):
            rank_combination_list = [0] + [(rank+1) for rank, _ in combination]
            sum_rank_point = sum([(10-rank) for rank, _ in combination])

            tmp_best_root = greedy(item_dict, rank_combination_list, moving_time, limit_time)
            if tmp_best_root and max_rank_point < sum_rank_point:
                max_rank_point = sum_rank_point
                best_root = tmp_best_root

    return best_root

def make_order_to_json(item_dict: dict, best_root: list) -> list:
    rout_list = []
    order = 1
    for rank in best_root:
        json_order = {"order": order, "id": item_dict[rank][0], "longitude": item_dict[rank][1], "latitude": item_dict[rank][2],  "place_name": item_dict[rank][4]}
        rout_list.append(json_order)
        order += 1
    return rout_list

def make_root(id_list: list, main_place_list: list, drive: bool, limit_time: float) -> list:
    item_dict = create_item_dict(id_list, main_place_list)
    moving_time = make_moving_time_list(item_dict, drive)
    best_root = try_all_combinations(item_dict, id_list, moving_time, limit_time)
    rout_list = make_order_to_json(item_dict, best_root)
    return rout_list

if __name__ == '__main__':
    id_list = [12,14,30,18,11,8,21,13,7,10]

    # ユーザーの入力
    main_place = (139.7677370730788,35.684187995344296) # 仮置き
    lon, lat = main_place
    main_place_name = "東京タワー"
    main_place_staying_time = 2 # [h]
    drive = False # 車か徒歩か
    limit_time = 8 # [h]

    main_place_list = [lon, lat, main_place_staying_time, main_place_name]
    item_dict = create_item_dict(id_list, main_place_list)
    moving_time = make_moving_time_list(item_dict, drive)
    best_root = try_all_combinations(item_dict, id_list, moving_time, limit_time)
    rout_list = make_order_to_json(item_dict, best_root)
    print(rout_list)