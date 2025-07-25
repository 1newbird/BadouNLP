import pandas as pd
from sklearn.model_selection import train_test_split
import json

# 读取 CSV 文件
df = pd.read_csv('data/文本分类练习.csv', header=None, names=['label', 'text'])

# 随机抽取 2000 条样本
df = df.sample(n=1000, random_state=42)

# 转换为指定格式的字符串，确保中文字符不被转义
df['formatted'] = df.apply(lambda row: json.dumps({"tag": row['label'], "content": row['text']}, ensure_ascii=False), axis=1)

# 划分训练集和验证集
train_df, val_df = train_test_split(
    df,
    test_size=0.2,      # 比如 20% 做验证集
    random_state=42,    # 固定随机种子，保证可复现
    shuffle=True        # 打乱
)

# 保存划分结果为 JSON 格式（每行一个 JSON 对象），直接写入文件而不是使用 to_csv
with open('data/train_data.json', 'w', encoding='utf-8') as f:
    for item in train_df['formatted']:
        f.write(f"{item}\n")

with open('data/val_data.json', 'w', encoding='utf-8') as f:
    for item in val_df['formatted']:
        f.write(f"{item}\n")

# 查看划分结果（可选）
print("训练集数量：", len(train_df))
print("验证集数量：", len(val_df))
