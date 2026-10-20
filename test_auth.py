"""验收脚本:JWT 认证五连测 —— 没票/假票/错密码都要被拦,对密码拿票后放行

运行方式:在【项目根目录】执行
    python test_auth.py
前提:uvicorn 已启动(8000 端口)
"""
import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000"


def post(path: str, body: dict, token: str = None):
    """发 POST;带票就放请求头。401 会抛 HTTPError,接住读错误详情"""
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


if __name__ == "__main__":
    print("① 裸调(不带票):")
    print("  ", post("/api/chat/agent", {"question": "你好"}))
    print("② 假票:")
    print("  ", post("/api/chat/agent", {"question": "你好"}, token="fake.token.here"))
    print("③ 错密码登录:")
    print("  ", post("/api/login", {"username": "admin", "password": "wrong"}))
    status, body = post("/api/login", {"username": "admin", "password": "admin123"})
    print("④ 对密码登录:", status, "→ 票前40字符:", body.get("token", "")[:40] + "...")
    token = body.get("token", "")
    print("⑤ 带真票问问题:")
    print("  ", post("/api/chat/agent",
                     {"session_id": "auth-test", "question": "年假有多少天?"},
                     token=token))
