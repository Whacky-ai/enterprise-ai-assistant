"""前台:FastAPI 网页接口 —— 把 chat.py 的大脑挂到网页上,人人可问

运行方式:在【项目根目录】执行
    python -m uvicorn main:app --reload
然后浏览器打开:
    http://127.0.0.1:8000/docs   ← FastAPI 免费送的测试网页,不用自己写前端
"""

# ==================== 块1:导入 ====================
from pydantic import BaseModel
from app.chat import answer
from fastapi.responses import StreamingResponse
from app.chat import answer_stream
from app.chat import answer_agent
from app.chat import get_history
from app.session_store import save_message
from app.redis_cache import cache_history
from app.auth import create_token, verify_token
from fastapi import HTTPException, FastAPI, Header, Depends
import jwt
from app.rate_limit import allow_request
# ==================== 块2:接待台开张 ====================
app = FastAPI(title="企业制度问答助手")
# ==================== 块3:快递单格式 ====================
class ChatRequest(BaseModel):
    question:str
    session_id:str = "default"
# ==================== 块4:服务窗口 ====================
@app.post("/api/chat")
def chat(req:ChatRequest):
    result = answer(req.question)
    return {"answer": result}

# ==================== 块5:流式窗口 ====================
def sse_wrap(question: str):
    for text in answer_stream(question):
        yield f"data: {text}\n\n"

@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    return StreamingResponse(sse_wrap(req.question),
                             media_type="text/event-stream")

# ==================== 块6:门厅(返回聊天网页) ====================
from fastapi.responses import FileResponse

@app.get("/")
def index():
    return FileResponse("static/index.html")

# ==================== 块9:门卫(验票放行) ====================
def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="没带门票")
    token = authorization.split(" ")[1]
    try:
        return verify_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="门票过期了,请重新登录")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="门票是假的")
    
# ==================== 块7:Agent 窗口 ====================
@app.post("/api/chat/agent")
def chat_agent(req: ChatRequest, user: str = Depends(get_current_user)):
    if not allow_request(user, 60, 60):
        raise HTTPException(status_code=429, detail="请求太频繁,请一分钟后再试")
    history = get_history(req.session_id)
    answer_text = answer_agent(req.question, history)
    save_message(req.session_id, "user", req.question)
    save_message(req.session_id, "assistant", answer_text)
    history.append(("user", req.question))
    history.append(("assistant", answer_text))
    cache_history(req.session_id, history)
    return {"answer": answer_text}

# ==================== 块8:登录窗口 ====================
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(req: LoginRequest):

    if req.username == "admin" and req.password == "admin123":
        token = create_token(req.username)
        return{"token":token}
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")