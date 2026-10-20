"""热缓存:速记本 —— 最近对话放 Redis,毫秒级读取

运行方式:在【项目根目录】执行
    python -m app.redis_cache      ← 自测:存 → 取 → 肉眼看

前提:Redis 服务已启动(redis-server.exe),.env 已配 REDIS_HOST/REDIS_PORT
"""

# ==================== 块1:连接(模块级全局,一次连好全程用) ====================
import redis
from app.config import REDIS_HOST, REDIS_PORT
import sys


r = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT,
    protocol=2,
    decode_responses=True
)
# ==================== 块2:存速记本 cache_history ====================
def cache_history(session_id: str, history: list):
    key = f"chat:{session_id}"
    r.delete(key)
    for role, content in history:
        r.rpush(key, f"{role}:{content}")
    r.expire(key, 1800)
# ==================== 块3:读速记本 get_cached_history ====================
def get_cached_history(session_id: str):
    key = f"chat:{session_id}"
    items = r.lrange(key, 0, -1)
    if not items:
        return None
    result = []
    for item in items:
        role, content = item.split(":", 1)
        result.append((role, content))
    return result
# ==================== 入口(自测) ====================
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cache_history("test-001", [("user", "你好"), ("assistant", "你好,我是企业AI助手")])
    print(get_cached_history("test-001"))
