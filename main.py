from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
import json

from fastapi import FastAPI, HTTPException, Depends, Request, Form, status
from fastapi.responses import RedirectResponse
from typing import Optional
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import APIRouter, Request, Form, Cookie, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

with open('key.json') as f:
    key_data = json.load(f)

url: str = key_data['supabase_url']
key: str = key_data['supabase_key']
supabase: Client = create_client(url, key)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

#sessionの準備
security = HTTPBasic()

class Item(BaseModel):
    id: str
    lon: float
    lat: float

class SessionData:
    def __init__(self):
        self.data = {}

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data.get(key)

session_data = SessionData()


@app.get("/")
async def read_root(request: Request):
    response = supabase.table('address').select("*").execute()
    context = {"request": request, "data": response.data}
    #print(response.data)
    return templates.TemplateResponse("index.html", context)

@app.post("/get_narrow")
async def narrow_down(request: Request):
    data=await request.json()
    lon=data.get("longitude")
    lat=data.get("latitude")
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
        lis.append((((row['longitude'] - lon)**2 + (row['latitude'] - lat)**2),row['id']))

    print()
    print(result)
    print("(距離,id)",lis)

    return json.dumps(result)#jsonに変換

@app.post("/main_place")
async def main2rank(request: Request):
    data=await request.json()
    id=data.get("id")
    lon=data.get("longitude")
    lat=data.get("latitude")

    #セッション（一時的に記憶）に登録
    id = session_data.get_data("id")
    lon = session_data.get_data("lon")
    lat = session_data.get_data("lat")
    if not id or not lon or not lat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found.")
    

    #/make-rankingにリダイレクト(クエリパラメータとして、最も行きたい場所の緯度経度を埋め込む)
    return RedirectResponse(url=f"/make-ranking?lon={session_data.lon}&lat={session_data.lat}")