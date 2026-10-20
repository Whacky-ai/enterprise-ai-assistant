"""问答模块:大脑上岗 —— 查资料 → 拼 prompt → DeepSeek 开卷答题

运行方式:在【项目根目录】执行
    python -m app.chat
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")  # 修复 Windows 控制台中文乱码

# ==================== 块1:导入 ====================
from langchain_openai import ChatOpenAI
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from app.rag import search
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from app.tools import query_attendance
from app.tools import search_documents
from app.redis_cache import get_cached_history
from app.session_store import load_history

# ==================== 块2:创建大脑连接 ====================
llm = ChatOpenAI(
    model = DEEPSEEK_MODEL,
    api_key = DEEPSEEK_API_KEY,
    base_url = DEEPSEEK_BASE_URL,
    temperature = 0
)
# ==================== 块3:拼 prompt ====================

def build_prompt(question: str, context_chunks: list[str]) -> str:
    """把资料和问题拼成一段 prompt(开卷考试的卷子)。"""
    context = "\n\n".join(context_chunks)
    prompt = f"""你是公司的规则制度管理员，只需要根据资料回答，没有就说不知道
=== 资料 ===
    {context}

=== 问题 === 
    {question}"""
    return prompt

# ==================== 块4:问答链路 ====================

def answer(question: str, top_k: int = 3) -> str:
    """完整链路:查资料 → 拼卷子 → 大脑答题。"""
    chunks = search(question, top_k)
    prompt = build_prompt(question, chunks)
    reply = llm.invoke(prompt)
    return reply.content

# ==================== 块5:流式问答 ====================
def answer_stream(question: str, top_k: int = 3):
    chunks = search(question, top_k)
    prompt = build_prompt(question, chunks)
    for chunk in llm.stream(prompt):
        yield chunk.content

#===========================================================
def get_history(session_id: str) -> list:
    history = get_cached_history(session_id)
    if history is None: history = load_history(session_id)
    return history

# ==================== 块6:Agent 版回答(两趟循环) ====================
llm_with_tools = llm.bind_tools([query_attendance, search_documents])
def answer_agent(question: str, history: list = None) -> str:
    messages = []
    if history:
        for role, content in history:
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=question))
    first = llm_with_tools.invoke(messages)
    if not first.tool_calls:
        return first.content
    messages.append(first)
    for call in first.tool_calls:
        if call["name"] == "query_attendance":
            result = query_attendance.invoke(call["args"])
        elif call["name"] == "search_documents":
            result = search_documents.invoke(call["args"])
        messages.append(ToolMessage(content=str(result),tool_call_id=call["id"]))

    second = llm_with_tools.invoke(messages)
    return second.content
# ==================== 入口 ====================

if __name__ == "__main__":
    print(answer("去上海出差,住酒店一晚预算多少?"))
    print(answer("迟到半小时会怎么处理?"))
    print(answer("年假有多少天?"))