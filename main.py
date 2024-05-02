from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
import json

with open('key.json') as f:
    key_data = json.load(f)

url: str = key_data['supabase_url']
key: str = key_data['supabase_key']
supabase: Client = create_client(url, key)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

#ベタ打ち（削除予定）
main_place=(139.405457,35.694031)#仮置き
lon,lat=main_place
n=0.1
print(main_place)
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
#ここまで


@app.get("/")
async def read_root(request: Request):
    response = supabase.table('address').select("*").execute()
    context = {"request": request, "data": response.data}
    #print(response.data)
    return templates.TemplateResponse("index.html", context)

@app.post("/")
async def narrow_down():
    main_place=(139.405457,35.694031)#仮置き
    lon,lat=main_place
    n=0.1
    print(main_place)
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

    return result
