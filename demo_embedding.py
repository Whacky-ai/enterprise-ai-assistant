"""第2步体验课:亲眼看看"意思相近 → 数字相近"
运行:python demo_embedding.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

from app.embedding import embed


def cos_sim(a, b):
    """余弦相似度:衡量两个向量的"方向接近程度"

    类比:两支箭指向越一致,值越接近 1;越无关,越接近 0。
    范围 -1 ~ 1,越大表示语义越相近。
    """
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


# 三句话:前两句意思相近,第三句无关
s1 = "差旅报销流程是什么"
s2 = "出差费用怎么报销"
s3 = "今天天气真不错"

vecs = embed([s1, s2, s3])

print(f"「{s1}」 vs 「{s2}」  相似度 = {cos_sim(vecs[0], vecs[1]):.3f}  ← 应该很高(意思相近)")
print(f"「{s1}」 vs 「{s3}」  相似度 = {cos_sim(vecs[0], vecs[2]):.3f}  ← 应该很低(毫无关系)")