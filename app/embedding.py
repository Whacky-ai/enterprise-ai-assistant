"""Embedding 模块:把文字变成"数字指纹"(向量)

类比:给每段文字拍一张"语义照片"。
- 意思相近的文字 → 照片长得像(数字距离近)
- 意思无关的文字 → 照片差别大(数字距离远)

为什么用本地模型(BAAI/bge-small-zh-v1.5)?
- 中文语义效果好,体积小(约 100MB)
- 本地运行:免费、不需要 API key、不联网也能用
"""
import os

# 国内访问 HuggingFace 会超时,改走镜像站 hf-mirror.com
# 注意:必须放在 import fastembed 之前,否则设置不生效
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
# 关闭 Xet 新传输通道(镜像站不代理它,会报 401),改走传统 HTTP 下载
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from fastembed import TextEmbedding

# 模块加载时就把模型读进内存(第一次运行会联网下载模型,之后走本地缓存)
_model = TextEmbedding("BAAI/bge-small-zh-v1.5")


def embed(texts: list[str]) -> list[list[float]]:
    """输入:文字列表 → 输出:向量列表(每条文字对应 512 个数字)

    用法:
        vecs = embed(["报销流程是什么", "考勤怎么打卡"])
        vecs[0]  # 第一条文字的向量
    """
    return [vec.tolist() for vec in _model.embed(texts)]