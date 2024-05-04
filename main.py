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

    print(lon,lat)
    """
    main_place=(139.405457,35.694031)#仮置き
    lon,lat=main_place
    """
    n=0.1
        # テーブル名と条件を指定
    table_name = 'address'

    # Supabaseのデータベースからデータを取得
    response = supabase.table(table_name).select('id', 'longitude', 'latitude').execute()
    print(response,type(response))
    #data,count = response
    data=response.data
    print(data)
        # 条件を満たすIDを取得
    result = [row['id'] for row in data if ((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2 <= n)]

    lis=[]
    for row in data:
        # lis.append((((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2),row['id']))
        lis.append(row['id'])
    print(result)
    print("(距離,id)",lis)

    return json.dumps(lis)#jsonに変換

# メインの場所を受け取って、リダイレクト
@app.post("/main_place")
async def main2rank(request: Request):
    data=await request.json()
    id=data.get("id")
    lon=data.get("longitude")
    lat=data.get("latitude")

    #セッション（一時的に記憶）に登録
    request.session["id"] = id
    request.session["lon"] = lon
    request.session["lat"] = lat
    if not id or not lon or not lat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found.")
    
    url = os.getenv("FRONTEND_URL")
    #/make-rankingにリダイレクト(クエリパラメータとして、最も行きたい場所の緯度経度を埋め込む)
    return RedirectResponse(url=f"{url}?lon={lon}&lat={lat}")


#ランキングの配列を受け取ってmap-rootにリダイレクト
@app.post("/accept_rank")
async def rank2route(request: Request):
    data=await request.json()
    #rank=json.loads(data)

    #アルゴリズム?

    #map-rootにリダイレクト
    #url = os.getenv("FRONTEND_URL")
    return data #RedirectResponse(url=f"{url}map-root/")

@app.get("/make_root")
async def read_root(request: Request):
    response = supabase.table('address').select("*").execute()
    context = {"request": request, "data": response.data}
    # 入れるデータの例:[2,4,12,18,11]
    # 出力されるデータの例:[{"order":1,"id":2,"longitude":139.405457,"latitude":35.694031},{"order":2,"id":4,"longitude":139.405457,"latitude":35.694031},{"order":3,"id":12,"longitude":139.405457,"latitude":35.694031},{"order":4,"id":42,"longitude":139.405457,"latitude":35.694031},{"order":5,"id":11,"longitude":139.405457,"latitude":35.694031}]
    # 最短ルート探索
    tmp_input_data = [2,4,12,18,11]
    root = make_root.make_root(tmp_input_data)
    print("作成したルート: ", root)
    # print(response.data)
    return templates.TemplateResponse("index.html", context)
=======
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

    print(lon,lat)
    """
    main_place=(139.405457,35.694031)#仮置き
    lon,lat=main_place
    """
    n=0.1
        # テーブル名と条件を指定
    table_name = 'address'

    # Supabaseのデータベースからデータを取得
    response = supabase.table(table_name).select('id', 'longitude', 'latitude').execute()
    print(response,type(response))
    #data,count = response
    data=response.data
    print(data)
        # 条件を満たすIDを取得
    result = [row['id'] for row in data if ((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2 <= n)]

    lis=[]
    for row in data:
        # lis.append((((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2),row['id']))
        lis.append(row['id'])
    print(result)
    print("(距離,id)",lis)

    return json.dumps(lis)#jsonに変換

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
@app.post("/accept_rank")
async def rank2route(request: Request):
    data=await request.json()
    #rank=json.loads(data)

    #アルゴリズム?
    
    #map-rootにリダイレクト
    #url = os.getenv("FRONTEND_URL")
    return data #RedirectResponse(url=f"{url}map-root/")





@app.get("/make_root")
async def read_root(request: Request):
    response = supabase.table('address').select("*").execute()
    context = {"request": request, "data": response.data}
    # 入れるデータの例:[2,4,12,18,11]
    # 出力されるデータの例:[{"order":1,"id":2,"longitude":139.405457,"latitude":35.694031},{"order":2,"id":4,"longitude":139.405457,"latitude":35.694031},{"order":3,"id":12,"longitude":139.405457,"latitude":35.694031},{"order":4,"id":42,"longitude":139.405457,"latitude":35.694031},{"order":5,"id":11,"longitude":139.405457,"latitude":35.694031}]
    # 最短ルート探索
    #root = make_root.make_root(response)

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
    # print(response.data)
    return json.dumps(root)

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
