from supabase import create_client, Client
import itertools
import json
import math

ONE_DEGREE = 111.321 # [km]
WALK_SPEED = 4 # [km/h]
DRIVE_SPEED = 34 # [km/h]
LIMIT_TIME = 8 #[h]

with open('key.json') as f:
    key_data = json.load(f)

url: str = key_data['supabase_url']
key: str = key_data['supabase_key']
supabase: Client = create_client(url, key)
response = supabase.table('address').select("*").execute()

def get_longitude_latitude_from_table(rank_list) -> dict:
    """
    return {rank: [id, longitude, latitude, staying_time], ...}
    """

    item_dict = {}
    rank = 1
    for item in response.data:
        id = item["id"]
        if id in rank_list:
            longitude = item["longitude"]
            latitude = item["latitude"]
            staying_time = item["staying_time"]
            item_dict[rank] =  [id, longitude, latitude, staying_time]
            rank += 1

    return item_dict

def calc_moving_time(rank1: list, rank2: list) -> float:
    distance = math.sqrt((rank1[1]-rank2[1])**2 + (rank1[2]-rank2[2])**2)
    moving_time = (distance * ONE_DEGREE) * 1.5 / DRIVE_SPEED
    return moving_time

def make_moving_time_list(item_dict: dict) -> list:
    N = len(item_dict)
    moving_time = [[0] * N for i in range(N)]

    for i in range(N):
        for j in range(N):
            moving_time[i][j] = moving_time[j][i] = calc_moving_time(item_dict[i+1], item_dict[j+1])
    return moving_time

def greedy(item_dict: dict, rank_list: list, moving_time: list) -> list:
    """
    return order list of rank
    ex: [2,1,5...] の時は、rank=2,1,5の順に回る
    """

    min_sum_time = LIMIT_TIME
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

def try_all_combinations(item_dict: dict, id_list: list, moving_time:list) -> list:
    best_root = []
    max_rank_point = 0
    for i in range(1, len(id_list)+1):
        for combination in itertools.combinations(enumerate(id_list),i):
            rank_combination_list = [(rank+1) for rank, _ in combination]
            sum_rank_point = sum([(10-rank) for rank, _ in combination])

            tmp_best_root = greedy(item_dict, rank_combination_list, moving_time)
            if tmp_best_root and max_rank_point < sum_rank_point:
                max_rank_point = sum_rank_point
                best_root = tmp_best_root
    return best_root

def make_order_to_json(item_dict: dict, best_root: list) -> list:
    rout_list = []
    order = 1
    for rank in best_root:
        json_order = {"order": order, "id": item_dict[rank][0], "longitude": item_dict[rank][1], "latitude": item_dict[rank][2]}
        rout_list.append(json_order)
        order += 1
    return rout_list

def make_root(id_list: list):
    item_dict = get_longitude_latitude_from_table(id_list)
    best_root = try_all_combinations(item_dict, id_list)
    rout_list = make_order_to_json(item_dict, best_root)
    return rout_list

if __name__ == '__main__':
    id_list = [2,4,12,18,11,8,1,13,5,10]
    item_dict = get_longitude_latitude_from_table(id_list)
    moving_time = make_moving_time_list(item_dict)
    best_root = try_all_combinations(item_dict, id_list, moving_time)
    rout_list = make_order_to_json(item_dict, best_root)
    print(rout_list)