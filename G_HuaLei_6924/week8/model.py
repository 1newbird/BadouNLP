# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from torch.optim import Adam, SGD
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

"""
建立网络模型结构
"""

class SentenceEncoder(nn.Module):
    def __init__(self, config):
        super(SentenceEncoder, self).__init__()
        hidden_size = config["hidden_size"]
        vocab_size = config["vocab_size"] + 1
        max_length = config["max_length"]
        self.embedding = nn.Embedding(vocab_size, hidden_size, padding_idx=0)
        # self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True, bidirectional=True)
        self.layer = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(0.5)

    # 输入为问题字符编码
    def forward(self, x):
        x = self.embedding(x)
        # 使用lstm
        # x, _ = self.lstm(x)
        # 使用线性层
        x = self.layer(x)
        x = nn.functional.max_pool1d(x.transpose(1, 2), x.shape[1]).squeeze()
        return x

class SiameseNetwork(nn.Module):
    def __init__(self, config):
        super(SiameseNetwork, self).__init__()
        self.sentence_encoder = SentenceEncoder(config)
        self.loss = nn.CosineEmbeddingLoss()

    # 计算余弦距离  1-cos(a,b)
    # cos=1时两个向量相同，余弦距离为0；cos=0时，两个向量正交，余弦距离为1
    def cosine_distance(self, tensor1, tensor2):
        tensor1 = torch.nn.functional.normalize(tensor1, dim=-1)
        tensor2 = torch.nn.functional.normalize(tensor2, dim=-1)
        cosine = torch.sum(torch.mul(tensor1, tensor2), dim=-1)
        return 1 - cosine

    def cosine_triplet_loss(self, a, p, n, margin=None):
        # 计算a和p的余弦距离
        ap = self.cosine_distance(a, p)
        # 计算a和n的余弦距离
        an = self.cosine_distance(a, n)
        # 如果没有设置margin，则使用经验值0.1
        if margin is None:
            # 张量/向量与 标量的运算，使用广播机制
            diff = ap - an + 0.1  # 0.1是经验值margin，防止an过大，ap-an过小
        else:
            # 否则使用传入的margin
            diff = ap - an + margin.squeeze()
        # 获取diff中大于0的元素
        new_diff = diff[diff.gt(0)]
        # 如果没有大于0的元素，则返回0
        if len(new_diff) == 0:
            return torch.tensor(0)
            # return torch.tensor(0.0, requires_grad=True)
        else:
            # 否则返回大于0的元素的平均值
            return torch.mean(new_diff)
        # return torch.mean(diff[diff.gt(0)])  # greater than

    # sentence : (batch_size, max_length)

    # def forward(self, sentence1, sentence2=None, target=None):
    #     #同时传入两个句子
    #     if sentence2 is not None:
    #         vector1 = self.sentence_encoder(sentence1) #vec:(batch_size, hidden_size)
    #         vector2 = self.sentence_encoder(sentence2)
    #         #如果有标签，则计算loss
    #         if target is not None:
    #             return self.loss(vector1, vector2, target.squeeze())
    #         #如果无标签，计算余弦距离
    #         else:
    #             return self.cosine_distance(vector1, vector2)
    #     #单独传入一个句子时，认为正在使用向量化能力
    #     else:
    #         return self.sentence_encoder(sentence1)

    def forward(self, sentence1, sentence2=None, sentenceAnchor=None):
        # 同时传入两个句子
        if sentence2 is not None:
            vector1 = self.sentence_encoder(sentence1)  # vec:(batch_size, hidden_size)
            vector2 = self.sentence_encoder(sentence2)
            # 如果有标签，则计算loss
            if sentenceAnchor is not None:
                vector3 = self.sentence_encoder(sentenceAnchor)
                return self.cosine_triplet_loss(vector3, vector1, vector2, torch.LongTensor([0.1]))
            # 如果无标签，计算余弦距离
            else:
                return self.cosine_distance(vector1, vector2)
        # 单独传入一个句子时，认为正在使用向量化能力
        else:
            return self.sentence_encoder(sentence1)

def choose_optimizer(config, model):
    optimizer = config["optimizer"]
    learning_rate = config["learning_rate"]
    if optimizer == "adam":
        return Adam(model.parameters(), lr=learning_rate)
    elif optimizer == "sgd":
        return SGD(model.parameters(), lr=learning_rate)

if __name__ == "__main__":
    from config import Config

    Config["vocab_size"] = 10
    Config["max_length"] = 4
    model = SiameseNetwork(Config)
    s1 = torch.LongTensor([[1, 2, 3, 0], [2, 2, 0, 0]])
    s2 = torch.LongTensor([[1, 2, 3, 4], [3, 2, 3, 4]])
    l = torch.LongTensor([[1], [0]])
    y = model(s1, s2, l)
    print(y)
    # print(model.state_dict())
