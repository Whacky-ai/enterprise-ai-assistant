"""会话存储:记忆本 —— 把每轮对话存进 MySQL 档案室

运行方式:在【项目根目录】执行
    python -m app.session_store      ← 自测:存两条 + 取出来看

前提:MySQL 服务已启动,库 assistant_db、表 messages 已建好,.env 里已配密码
"""

# ==================== 块1:开门 get_conn ====================
import pymysql
from app.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
import sys

def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST,       
        port=MYSQL_PORT,      
        user=MYSQL_USER,        
        password=MYSQL_PASSWORD,  
        database=MYSQL_DB,        
        charset="utf8mb4"
    )

# ==================== 块2:存一条 save_message ====================
def save_message(session_id: str, role: str, content: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()
# ==================== 块3:取最近N条 load_history ====================
def load_history(session_id: str, limit: int = 20) -> list:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM messages WHERE session_id=%s ORDER BY id DESC LIMIT %s",
        (session_id, limit)
    )
    rows = list(cur.fetchall())
    conn.close()
    rows.reverse()
    return rows
# ==================== 入口(自测) ====================
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    save_message("test-001", "user", "你好")
    save_message("test-001", "assistant", "你好,我是企业AI助手")
    history = load_history("test-001")
    print(history)