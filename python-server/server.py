from fastapi import FastAPI, Depends, Request
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.semconv.trace import SpanAttributes

from time import time
import asyncio
import logging, aiohttp, json

from sqlalchemy.orm import Session

import util.telemetry
from util import telemetry, aiohttp_request
from util.db import get_db, Students
from util.redis_db import client
from util.counter import Counter


# 创建 FastAPI 应用
app = FastAPI()

# 启动时的初始化
telemetry.init_trace(util.telemetry.fastapi_service_name)
telemetry.init_log(util.telemetry.fastapi_service_name)
telemetry.init_metric(util.telemetry.fastapi_service_name)
aiohttp_request.init_aiohttp_client()
# 在初始化 OpenTelemetry 提供者后进行应用程序的自动仪器化
FastAPIInstrumentor.instrument_app(app)

# 数据统计
util_count = Counter(service_name=util.telemetry.fastapi_service_name)
# 自定义中间件
@app.middleware("http")
async def telemetry_middleware(req: Request, call_next):
    attributes = {
        SpanAttributes.HTTP_ROUTE: req.url.path,
        SpanAttributes.HTTP_REQUEST_METHOD: req.method,
    }
    # 增加活跃请求计数器
    util_count.request_active_counter.add(1, attributes)
    # 记录请求开始时间
    start_time = time()
    try:
        # 调用下一个中间件或路由处理函数
        response = await call_next(req)
        return response
    finally:
        # 计算请求持续时间
        duration = (time() - start_time) * 1000  # 转换为毫秒
        # 记录请求持续时间到直方图
        util_count.request_duration_histogram.record(duration, attributes)
        # 减少活跃请求计数器
        util_count.request_active_counter.add(-1, attributes)
        # 增加请求总数计数器
        util_count.request_counter.add(1, attributes)

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
    uvicorn.run('server:app', host="0.0.0.0", port=5000, workers=2, loop='uvloop')
