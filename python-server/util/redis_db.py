import redis
from opentelemetry.instrumentation.redis import RedisInstrumentor

client = redis.Redis(host='localhost', port=6379)

def request_hook(span, instance, args, kwargs):
    if span is None:
        return

    command = args[0]
    parameters = args[1:]
    # 构建完整的 Redis 命令字符串
    command_with_args = ' '.join([command] + [str(param) for param in parameters])
    # 将完整的命令设置为 db.statement 属性
    span.set_attribute("db.statement", command_with_args)
    span.set_attribute("db.redis.command", command)
    span.set_attribute("db.redis.args", parameters)

# 对特定的客户端实例进行仪器化
RedisInstrumentor().instrument(request_hook=request_hook)
