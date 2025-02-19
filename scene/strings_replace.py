# iOS 字符串替换的值
import json
import os
import re

from localization.localization import get_localized_text
from utils.cache_utils import load_from_cache, save_to_cache
from utils.file_utils import select_source, find_folders_with_files


def get_strings_replace_history_cache(cache_json):
    """获取历史的存储记录"""
    if not cache_json or not cache_json.get("stringsReplace"):
        # 如果没有缓存或 `podfileCommand` 数据缺失
        path, result = get_folder_path()
        cache_json = get_init_exc_path(cache_json, key=path, value=result)
        if not path:
            return None  # 用户取消操作
    else:
        return cache_json["stringsReplace"]

    return cache_json["stringsReplace"]


def get_folder_path():
    """
    获取选中的目录并且返回执行的文件列表
    """
    strings_folder_path = select_source(only_folder=True)
    if not strings_folder_path:
        print(get_localized_text("no_choose_tip"))
        return None, None
    result = find_folders_with_files(strings_folder_path, file_suffixes='.strings')
    new_list = []
    rootCount = strings_folder_path.count("/")
    for item in result:
        if item.count("/") == rootCount + 1 and item.find(".lproj") != -1:
            new_list.append(item)

    return strings_folder_path, new_list


def get_init_exc_path(orgDict=None, key=None, value=None):
    if key is None or value is None:
        return None
    data = {
        "stringsReplace": {
            key: value,
        }
    }
    if orgDict is None:
        return data
    # 将新数据合并到 orgDict 中
    orgDict.update(data)
    return orgDict


def get_execute_folders(result, cache_json, first=False):
    """获取执行的目录列表"""
    index = 1
    keys = []
    for key, value in result.items():
        print(get_localized_text("execution_path", num=index, path=key))
        keys.append(key)
        index += 1
    if len(result) == 1 and first:
        return cache_json, result[keys[0]]
    input_num = input(get_localized_text("choose_path_no_tip")).strip()
    try:
        if int(input_num) > len(result):
            print(get_localized_text("please_valid_number"))
            get_execute_folders(result)
        else:
            if int(input_num) == 0:
                path, result = get_folder_path()
                new_json = get_init_exc_path(cache_json, key=path, value=result)
                return new_json, result
            else:
                choose_key = keys[int(input_num) - 1]
                return cache_json, result[choose_key]
    except ValueError:
        print(get_localized_text("please_valid_number"))
        get_execute_folders(result)


def execute_replace(cache_json, folder_list):
    """
    执行替换的操作
    """
    # 设置规则(开始将文件内的内容替换) JSON 字典类型， key为原本文件中的关键字, value 为替换后的值
    # rule = {"clickfree": "AI-Xpander", "Clickfree": "AI-Xpander", "ClickFree": "AI-Xpander"}
    # '{"clickfree": "AI-Xpander", "Clickfree": "AI-Xpander", "ClickFree": "AI-Xpander"}'
    rule = input("请输入需要替换的json 字典: key 为源文件的关键字 value为替换后的内容(替换区分大小写):")
    try:
        rule = json.loads(rule)  # 尝试解析 JSON
        if not isinstance(rule, dict):
            print("❌ rule 不是一个 JSON 字典")
            return
    except json.JSONDecodeError:
        print("❌ rule 不是有效的 JSON 格式")
        return

    for folder in folder_list:
        file_path = os.path.join(folder, "Localizable.strings")
        # 读取文件内容
        if not os.path.exists(file_path):
            print(f"文件 {file_path} 不存在，跳过")
            continue
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            # 处理每一行内容
        new_lines = []
        for line in lines:
            # 正则匹配 key 和 value
            match = re.match(r'^(.*?)\s*=\s*"(.*)";$', line)
            if match:
                key = match.group(1)  # key 保持不变
                value = match.group(2)  # 提取原始值

                # 进行替换
                for old, new in rule.items():
                    value = value.replace(old, new)

                # 重新构造字符串
                new_lines.append(f'{key} = "{value}";\n')
            else:
                new_lines.append(line)  # 其他内容保持不变

        # 写入修改后的内容到 **原文件**
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(new_lines)

        print(f"文件 {file_path} 处理完成 ✅")


def run_strings_replace():
    """读取文件列表"""
    cache_json = load_from_cache()
    # 如果是初次选择的情况下不再让用户选择输入其他编号
    isFirst = cache_json is None or not cache_json.get("stringsReplace")

    # 获取 Strings的 路径
    result = get_strings_replace_history_cache(cache_json)
    if cache_json is None:
        cache_json = {"stringsReplace": result}
    if result is None:
        print(get_localized_text("cancel_choose_tip"))
        return
    cache_json, folder_list = get_execute_folders(result, cache_json, isFirst)
    if folder_list is None:
        print(get_localized_text("cancel_choose_tip"))
        return
    save_to_cache(cache_json)
    execute_replace(cache_json, folder_list)
