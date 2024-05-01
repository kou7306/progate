from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
import json
import make_root

with open('key.json') as f:
    key_data = json.load(f)

url: str = key_data['supabase_url']
key: str = key_data['supabase_key']
supabase: Client = create_client(url, key)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request):
    response = supabase.table('address').select("*").execute()
    context = {"request": request, "data": response.data}
    # 最短ルート探索
    root = make_root.make_root(response)
    print("作成したルート: ", root)
    # print(response.data)
    return templates.TemplateResponse("index.html", context)