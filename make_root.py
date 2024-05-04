def make_root(rank_list):
    ans = []
    for i in range(len(rank_list)):
        ans.append({"id" : rank_list[i], "latitude": 135, "longitude": 35, "order": i})
    return {"root": ans}