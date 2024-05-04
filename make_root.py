from supabase import create_client, Client
import json
import math

with open('key.json') as f:
    key_data = json.load(f)

url: str = key_data['supabase_url']
key: str = key_data['supabase_key']
supabase: Client = create_client(url, key)

def get_longitude_latitude_from_table(response):
    """
    return {id: [longitude, latitude]}
    """

    item_d = {}
    for item in response.data:
        #print(item)
        id = item["id"]
        longitude = item["longitude"]
        latitude = item["latitude"]
        item_d[id] =  [longitude, latitude]
    return item_d

def distance(location1, location2):
    return math.sqrt((location1[0]-location2[0])**2 + (location1[1]-location2[1])**2)

def greedy(locations):
    """
    return order list 
    """
    N = len(locations)
    dist = [[0] * N for i in range(N)]
    #print(locations[1])
    #print(locations[N])

    for i in range(N):
        for j in range(N):
            dist[i][j] = dist[j][i] = distance(locations[i+1],locations[j+1])
    #print(dist)

    min_sum_distance = float('inf')
    best_root = []
    for i in range(N):
        tmp_sum_distance = 0
        current_location = i
        unvisited_locations = set(range(N))
        unvisited_locations.remove(i)

        root = [current_location]
        #print(root)
        while unvisited_locations:
            next_location = min(unvisited_locations, key=lambda location: dist[current_location][location])
            unvisited_locations.remove(next_location)
            root.append(next_location)
            tmp_sum_distance += dist[current_location][next_location]
            current_location = next_location
        
        #print("root ", i, " :", root)
        #print(tmp_sum_distance)

        if tmp_sum_distance < min_sum_distance:
            best_root = root
            min_sum_distance = tmp_sum_distance

    return best_root

def make_json_for_root(best_root):
    """
    {"root": [{"id": i, "order": j} ..... ]}
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