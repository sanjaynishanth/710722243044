from fastapi import FastAPI,HTTPException
import  requests
import redis
import json
app=FastAPI()

redis_client=redis.Redis(host="localhost",port=6379, db=0,decode_responses=True)

external_api="http://20.244.56.144/test/users "


@app.get("/products/{company}/{category}")

def get_top_products(company:str,category:str,top:int):
    