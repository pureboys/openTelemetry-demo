import json
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor

# 定义自定义的请求钩子函数
def request_hook(span, params):
    if span is None:
        return

    # 获取请求的 URL 和方法
    url = params.url
    method = params.method

    # 记录请求方法和完整 URL
    span.set_attribute("http.method", method)
    span.set_attribute("http.url", str(url))

    # 记录查询参数
    query_params = dict(url.query)
    if query_params:
        span.set_attribute("http.request.query_params", json.dumps(query_params))

    # 记录请求头（注意避免记录敏感信息）
    headers = params.headers
    if headers:
        sanitized_headers = {k: v for k, v in headers.items() if k.lower() != 'authorization'}
        span.set_attribute("http.request.headers", json.dumps(sanitized_headers))

# 使用 AioHttpClientInstrumentor 自动为 aiohttp 客户端添加 OpenTelemetry 支持
AioHttpClientInstrumentor().instrument(request_hook=request_hook)
