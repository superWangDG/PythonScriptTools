# 用于缓存数据

import json


def save_to_cache(data, file_path=".cache.json"):
    """将数据保存到本地缓存文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_from_cache(file_path=".cache.json"):
    """从本地缓存文件加载数据"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None