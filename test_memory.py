"""验收脚本:多轮记忆测试 —— 用"代词"考 Agent 记不记得上一轮
(2026-09-20 适配 JWT:先登录拿票,带票调用)

运行方式:在【项目根目录】执行
    python test_memory.py
前提:uvicorn 已启动(8000 端口)
"""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")


def ask(session_id: str, question: str, token: str) -> str:
    data = json.dumps({"session_id": session_id, "question": question}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/chat/agent",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",   # 带票进门
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["answer"]


if __name__ == "__main__":
    # 先登录拿票
    login_data = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/login",
        data=login_data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        token = json.loads(resp.read().decode("utf-8"))["token"]
    print("已登录拿票,开始测试")

    sid = "exam-docker"
    print("=" * 50)
    print("第1问:张三这个月迟到了几次?")
    print("答:", ask(sid, "张三这个月迟到了几次?", token))
    print("=" * 50)
    print("第2问(代词测试):那他早退呢?")
    print("答:", ask(sid, "那他早退呢?", token))
    print("=" * 50)
