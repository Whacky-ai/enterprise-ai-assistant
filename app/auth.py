"""认证模块:签票员 —— 登录成功发 JWT 门票,验票辨真假

运行方式:在【项目根目录】执行
    python -m app.auth          ← 自测:签一张票 → 验它 → 故意改坏再验

前提:.env 已配 JWT_SECRET_KEY、JWT_EXPIRE_MINUTES(见 config.py)
"""

# ==================== 块1:导入 ====================
import jwt
from datetime import datetime, timedelta, timezone
from app.config import JWT_SECRET_KEY, JWT_EXPIRE_MINUTES
import sys


# ==================== 块2:签票 create_token ====================
def create_token(username: str) -> str:
    """登录成功 → 把票主+有效期写进 payload,盖上密钥水印"""
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


# ==================== 块3:验票 verify_token ====================
def verify_token(token: str) -> str:
    """验票:水印真 → 返回票主名;假票/过期 → jwt 自动抛异常(信号弹,给调用方处理)"""
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    return payload["sub"]

# ==================== 入口(自测) ====================
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    token = create_token("admin")
    print("签的票:", token)
    print("验票结果：", verify_token(token))
    try:
        verify_token(token + "x")
    except jwt.InvalidTokenError as e:
        print("坏票被识破,异常类型：", type(e).__name__)
