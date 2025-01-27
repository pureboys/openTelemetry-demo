from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import logging
from util import telemetry

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


# 运行应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
