"""RAG 模块:公司的"资料室"

三大能力(分两次实现):
1. split_text   —— 长文档切成 ~200 字的片段          ← 本文件实现
2. add_document —— 片段 → 向量 → 存进 Chroma        ← 本文件实现
3. search       —— 按相似度挑最相关的片段            ← 任务C2再加

运行方式:在【项目根目录】执行
    python  -m app.rag
"""

# ==================== 块1:导入 ====================
from chromadb import PersistentClient
from app.embedding import embed
import os

# ==================== 块2:连接 Chroma ====================
_client = PersistentClient(path="chroma_data")
_collection = _client.get_or_create_collection("company_docs")

# ==================== 块3:切片 ====================

def split_text(text: str, chunk_size: int = 200) -> list[str]:
    chunks = []
    paras = text.split("\n\n")

    for para in paras:
        para = para.strip()
        if not para:
            continue
        if len(para) <= chunk_size:
            chunks.append(para)
        else:
            sentences = para.split("。")
            current = ""
            for s in sentences:
                if not s:
                    continue
                piece = s + "。"
                if len(current) + len(piece) > chunk_size:
                    if current:
                        chunks.append(current)
                    current = ""
                current += piece
            if current:          
              chunks.append(current)
    return chunks
# ==================== 块4:入库 ====================

def add_document(filepath: str) -> int:
    """
    流程四步:读文件 → split_text → embed → collection.add
    """
    text = open(filepath, encoding="utf-8").read()
    chunks = split_text(text)
    vectors = embed(chunks)
    name = os.path.basename(filepath)
    ids = [f"{name}-{i}" for i in range(len(chunks))]
    _collection.add(ids=ids, documents=chunks, embeddings=vectors)
    print(f"已入库 {len(chunks)}片:{name}")
    return len(chunks)
# ==================== 块5:检索 ====================

def search(query: str, top_k: int = 3) -> list[str]:
    """按语义相似度,从资料室挑出最相关的 top_k 个片段。

    流程三步:问题 → 向量 → 查档案柜 → 返回片段文本列表
    """
    q_vec = embed([query])[0]
    res = _collection.query(query_embeddings=q_vec, n_results=top_k)
    return res["documents"][0]
    
# ==================== 入口 ====================

if __name__ == "__main__":
    add_document("docs/差旅报销制度.md")
    add_document("docs/考勤管理制度.md")
    print(_collection.count())