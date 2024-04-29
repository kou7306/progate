from fastapi import FastAPI
from supabase import create_client, Client
import json

with open('key.json') as f:
    key_data = json.load(f)
    
url: str = key_data['supabase_url']
key: str = key_data['supabase_key']
supabase: Client = create_client(url, key)
app = FastAPI()

@app.get("/")
async def read_root():
    response = supabase.table('address').select("*").execute()
    return response.data