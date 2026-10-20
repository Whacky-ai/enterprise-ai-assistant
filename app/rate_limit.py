"""限流模块:额度卡 —— Redis 原子计数,一分钟最多 N 次,超了拒

运行方式:在【项目根目录】执行
    python -m app.rate_limit      ← 自测:连发 65 次,看第 61 次开始被拒
前提:Redis 服务已启动(redis-server.exe)
"""
import sys

from app.redis_cache import r     # 复用模块级的 r 连接,不重复开门


# ==================== 块1:额度卡 allow_request ====================
def allow_request(user_id: str, limit: int = 60, window: int = 60) -> bool:
    """每个用户一把计数尺:窗口内次数 ≤ limit 放行(True),超了拒(False)"""
    key = f"rate:{user_id}"
    count = r.incr(key)
    if count == 1: r.expire(key, window)
    return count <=limit


# ==================== 入口(自测) ====================
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    r.delete("rate:test-user")          
    for i in range(1, 66):              
        ok = allow_request("test-user")
        if i >= 61:                     
            print(f"第{i}次:", ok)

    
