from urllib import request
from fastapi import FastAPI, Depends, HTTPException, status,Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
import json
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import make_root

load_dotenv()
# CORS 設定
origins = [
    "https://progate-hackathon-frontend.vercel.app",
    "http://localhost:3000",
]




with open('key.json') as f:
    key_data = json.load(f)

url: str = key_data['supabase_url']
key: str = key_data['supabase_key']
supabase: Client = create_client(url, key)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
# #sessionの準備
app.add_middleware(SessionMiddleware, secret_key="topsecret")


# test
@app.get("/")
async def read_root(request: Request):
    response = supabase.table('address').select("*").execute()
    context = {"request": request, "data": response.data}
    #print(response.data)
    return templates.TemplateResponse("index.html", context)

# 候補の場所を渡す
@app.post("/get_narrow")
async def narrow_down(request: Request):
    
    response=await request.json()
    print(response) 
    lon=response['data']['longitude']
    lat=response['data']['latitude']
    lon = float(lon)
    lat = float(lat)
    tra=response['transportation']#徒歩は0,車は１
    print(lon,lat)
    """
    main_place=(139.405457,35.694031)#仮置き
    lon,lat=main_place
    """

    if tra:    
        n=0.021#車で30分くらい
    else: 
        #n=0.0013 #徒歩1時間くらい
        n=0.006 #徒歩2時間くらい

            # テーブル名と条件を指定
    table_name = 'address'

    # Supabaseのデータベースからデータを取得
    response = supabase.table(table_name).select('id', 'longitude', 'latitude').execute()
    #print(response,type(response))
    #data,count = response
    data=response.data
    #print(data)
            # 条件を満たすIDを取得
    result = [row['id'] for row in data if ((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2 <= n)]


    print('res',result)
    print(len(result))

    #候補地が多いとき
    k =30  #候補地の数の限界値
    if len(result)>=k:
        lis=[]
        for row in data:
            #print(row)
            lis.append((((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2),row['id']))
        #print(lis)
        lis.sort()
        #print(lis)
        res=[]
        for i in lis[:k]:
            res.append(i[1])
        result=res
    #print("(距離,id)",lis)
    print('res_kai',result)
    print(len(result))
    return json.dumps(result)#jsonに変換

# メインの場所を受け取って、リダイレクト
# @app.post("/main_place")
# async def main2rank(request: Request):
#     data=await request.json()
#     id=data.get("id")
#     lon=data.get("longitude")
#     lat=data.get("latitude")

#     #セッション（一時的に記憶）に登録
#     request.session["id"] = id
#     request.session["lon"] = lon
#     request.session["lat"] = lat
#     if not id or not lon or not lat:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found.")
    
#     url = os.getenv("FRONTEND_URL")
#     #/make-rankingにリダイレクト(クエリパラメータとして、最も行きたい場所の緯度経度を埋め込む)
#     return RedirectResponse(url=f"{url}?lon={lon}&lat={lat}")


#ランキングの配列を受け取ってmap-rootにリダイレクト

@app.post("/make_root")
async def read_root(request: Request):
    items = await request.json()
    # リクエストボディからデータを取得

    number_items = list(map(int, items))

    print("number_list: ", number_items)
    
    # 入れるデータの例:[2,4,12,42,11]
    # 出力されるデータの例:[{"order":1,"id":2,"longitude":139.405457,"latitude":35.694031},{"order":2,"id":4,"longitude":139.405457,"latitude":35.694031},{"order":3,"id":12,"longitude":139.405457,"latitude":35.694031},{"order":4,"id":42,"longitude":139.405457,"latitude":35.694031},{"order":5,"id":11,"longitude":139.405457,"latitude":35.694031}]
    # 最短ルート探索
    root = make_root.make_root(number_items)
    print("root: ", root)

    # root=[
    #     {
    #     'number': 1, 
    #     'address': "東京都台東区上野公園９−８３", 
    #     'lat': 35.7181172305638, 
    #     'lng': 139.773761356751 
    #     },
    #     {
    #     'number': 2, 
    #     'address': "東京都江東区豊洲６丁目６−１", 
    #     'lat': 35.6461239098884, 
    #     'lng': 139.784210093853 
    #     },
    #     {
    #     'number': 3, 
    #     'address': "東京都中央区佃２丁目１", 
    #     'lat': 35.6726742311275, 
    #     'lng': 139.786473177283 
    #     },
    #     {
    #     'number': 4, 
    #     'address': "東京都葛飾区柴又７丁目", 
    #     'lat': 35.7619694606295, 
    #     'lng': 139.876150947625 
    #     }
    # ]
    return {"root": root}



main_place=(139.7677370730788,35.684187995344296)#仮置き
lon,lat=main_place
tra=1
#print("a")
#print((139.7980772673309-139.82533008204277)**2+(35.680485755979404-35.704111613579826)**2)
print((139.7827435599349-139.8779397301384)**2+(35.644980620033785-35.75608680900554)**2)
if tra:    
    n=0.021
else: 
    #n=0.0013 #徒歩1時間くらい
    n=0.006 #徒歩2時間くらい

        # テーブル名と条件を指定
table_name = 'address'

# Supabaseのデータベースからデータを取得
response = supabase.table(table_name).select('id', 'longitude', 'latitude').execute()
#print(response,type(response))
#data,count = response
data=response.data
#print(data)
        # 条件を満たすIDを取得
result = [row['id'] for row in data if ((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2 <= n)]


print('res',result)
print(len(result))

#候補地が多いとき
k =30  #候補地の数の限界値
if len(result)>=k:
    lis=[]
    for row in data:
        #print(row)
        lis.append((((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2),row['id']))
    #print(lis)
    lis.sort()
    #print(lis)
    res=[]
    for i in lis[:k]:
        res.append(i[1])
    result=res
#print("(距離,id)",lis)
print('res_kai',result)
print(len(result))


#テストデータのテスト
"""
root=[
        {
        'number': 1, 
        'address': "東京都台東区上野公園９−８３", 
        'lat': 35.7181172305638, 
        'lng': 139.773761356751 
        },
        {
        'number': 2, 
        'address': "東京都江東区豊洲６丁目６−１", 
        'lat': 35.6461239098884, 
        'lng': 139.784210093853 
        },
        {
        'number': 3, 
        'address': "東京都中央区佃２丁目１", 
        'lat': 35.6726742311275, 
        'lng': 139.786473177283 
        },
        {
        'number': 4, 
        'address': "東京都葛飾区柴又７丁目", 
        'lat': 35.7619694606295, 
        'lng': 139.876150947625 
        }

    ]
print("作成したルート: ", root)
print(type(root))
print(root[1])
print(type(root[1]))
rootj=json.dumps(root)
print(rootj)
print(type(rootj))

"""