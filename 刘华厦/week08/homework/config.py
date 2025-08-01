# -*- coding: utf-8 -*-

"""
配置参数信息
"""

Config = {
    "model_path": "model_output",
    "schema_path": "../data/schema.json",
    "train_data_path": "../data/train.json",
    "valid_data_path": "../data/valid.json",
    "vocab_path": "./chars.txt",
    "max_length": 20,
    "hidden_size": 128,
    "epoch": 20,
    "batch_size": 32,
    "epoch_data_size": 1000,  # 每轮训练中采样数量
    "optimizer": "adam",
    "learning_rate": 1e-3,
    "triplet_loss_margin": 0.3,  # 三元组的超参数
}
