from fastapi import FastAPI, Depends
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import asyncio
import logging, aiohttp, json

from sqlalchemy.orm import Session
from util import telemetry, request
from util.db import get_db, Students
from util.redis_db import client

# 初始化日志和跟踪
telemetry.init_trace()
telemetry.init_log()

# 创建 FastAPI 应用
app = FastAPI()
# 使用 FastAPIInstrumentor 自动为 FastAPI 应用添加 OpenTelemetry 支持
FastAPIInstrumentor.instrument_app(app)


# 定义一个简单的路由
@app.get("/")
async def read_root():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("read_root_span"):
        my_log = logging.getLogger("read_root_span")
        my_log.info("read_root!")
        return {"message": "Hello, World!"}


@app.get("/get_db")
async def get_db(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(Students).offset(skip).limit(limit).all()
    logging.info(f"get_db ...")
    return users


@app.get("/get_redis")
async def get_redis():
    key1 = client.get("key1")
    return {"data": key1}


@app.get("/do_request")
async def do_request():
    logging.info(f"do_request ...")
    urls = [
        "http://baike.baidu.com/api/openapi/BaikeLemmaCardApi?scope=103&format=json&appid=379020&bk_key=关键字&bk_length=600",
        "http://baike.baidu.com/api/openapi/BaikeLemmaCardApi?scope=103&format=json&appid=379020&bk_key=关键字&bk_length=600",
        "http://baike.baidu.com/api/openapi/BaikeLemmaCardApi?scope=103&format=json&appid=379020&bk_key=关键字&bk_length=600",
    ]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return {"data": responses}

async def fetch(session, url):
    async with session.get(url, timeout=10) as response:
        if response.status == 200:
            res = await response.text('utf-8')
            return json.loads(res)
        else:
            return {"error": f"Failed to fetch {url}"}

# 运行应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
