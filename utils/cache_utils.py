# 用于缓存数据

import json

from localization.localization import get_localized_text
from utils.file_utils import select_source


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


def get_list_use_folder_cache(cache_json, main_key):
    """获取缓存的文件夹`cache_json`缓存的原始JSON, `main_key` 存储模块的关键字"""
    if not cache_json or not cache_json.get(main_key):
        # 如果没有缓存或 `podfileCommand` 数据缺失
        exc_path = select_source(only_folder=True)
        if not exc_path:
            return None  # 用户取消操作
        cache_json.update({
            main_key: [exc_path]
        })
        save_to_cache(cache_json)
        return exc_path
    else:
        cache_paths = cache_json[main_key]
        for index, item in enumerate(cache_paths):
            print(get_localized_text("execution_path", path=item, num=index+1))
        text = input(get_localized_text("choose_path_no_tip")).strip()
        try:
            int_number = int(text)
            if int_number == 0:
                exc_path = select_source(only_folder=True)
                if not exc_path:
                    return None  # 用户取消操作
                # 追加地址
                cache_paths.append(exc_path)
                cache_json[main_key] = cache_paths
                save_to_cache(cache_json)
                return exc_path
            else:
                # 返回当前选择下标的数据
                return cache_paths[int_number - 1]
        except ValueError:
            print(f"无法将 '{text}' 转换为整数。")
