"""第1步里程碑:验证 DeepSeek 连通性
运行:python test_llm.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")  # 修复 Windows 控制台中文乱码

from langchain_openai import ChatOpenAI

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

if not DEEPSEEK_API_KEY:
    print("[错误] 请先复制 .env.example 为 .env,并填入你的 DEEPSEEK_API_KEY")
    exit(1)

# 类比:和 redis.Redis() 一样——创建连接对象 → 调方法
llm = ChatOpenAI(
    model=DEEPSEEK_MODEL,
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    temperature=0,  # 稳定一致的输出
)

resp = llm.invoke("什么是RAG?用3行以内解释")
print("[OK] LLM 回复:", resp.content)
