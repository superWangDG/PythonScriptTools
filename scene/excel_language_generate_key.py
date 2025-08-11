import os
import re
import shutil

import pandas as pd

from localization.localization import get_localized_text
from utils.cache_utils import get_list_use_folder_cache, load_from_cache
from utils.file_utils import find_exc_file, open_folder

def clean_to_english_text(text: str) -> str:
    """清理掉非英文字符（包括 emoji、中文等），仅保留英文、数字、空格"""
    # 去掉 emoji 和非基本字符（unicode > U+FFFF 的通常是 emoji）
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    # 去掉中文
    text = re.sub(r'[\u4e00-\u9fff]', '', text)
    # 去掉标点符号，保留英文/数字/空格
    text = re.sub(r'[^a-zA-Z0-9 ]+', '', text)
    return text.strip()

def generate_lang_key(text: str) -> str:
    """将英文文本转为 key 格式：小写、空格变下划线"""
    cleaned = clean_to_english_text(text)
    if not re.search(r'[a-zA-Z]', cleaned):  # 没有英文就返回空
        return ""
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned.lower()

def start_run_generate_key(excel_path, output_directory):
    df = pd.read_excel(excel_path, header=None)

    # 找到 "Key" 所在行列
    key_row_idx = None
    key_col_idx = None
    for row_idx, row in df.iterrows():
        for col_idx, val in row.items():
            if isinstance(val, str) and val.strip().lower() == "key":
                key_row_idx = row_idx
                key_col_idx = col_idx
                break
        if key_row_idx is not None:
            break

    if key_row_idx is None:
        print("❌ 未找到 'Key' 标识行")
        return

    # 找包含 'english' 的列
    english_col_idx = None
    for col_idx, val in df.loc[key_row_idx].items():
        if isinstance(val, str) and "english" in val.lower():
            english_col_idx = col_idx
            break

    if english_col_idx is None:
        print("❌ 未找到包含 'english' 的语言列")
        return

    # 设置表头
    df.columns = df.iloc[key_row_idx]
    df = df.iloc[key_row_idx + 1:].reset_index(drop=True)

    english_col_name = df.columns[english_col_idx]

    keys = []
    for _, row in df.iterrows():
        text = str(row[english_col_name])
        key = generate_lang_key(text)
        # 关键字拦截
        if key == 'in':
            key = 'i_n'
        keys.append(key)

    df['Key'] = keys

    # 输出文件
    filename = os.path.basename(excel_path)
    output_file = os.path.join(output_directory, f"key_generated_{filename}")
    df.to_excel(output_file, index=False)
    print(f"✅ 已生成并写入 key：{output_file}")


def run_excel_language_generate_key():
    # 加载缓存
    result = get_list_use_folder_cache(load_from_cache(), "LanguageGenerateKey")
    if not result:
        print(get_localized_text("cancel_choose_tip"))
        return
    print("选择表格文件")
    exc_path = find_exc_file(result, '.xlsx')

    output_path = os.path.splitext(exc_path)[0]
    output_directory = os.path.join(output_path, "output")
    if os.path.exists(output_directory):
        # 如果文件夹存在删除文件夹
        try:
            shutil.rmtree(output_directory)  # 递归删除文件夹及其内容
        except Exception as e:
            print(get_localized_text("delete_folder_failed", error=str(e)))

    os.makedirs(output_directory)
    # 开始执行操作
    print(get_localized_text("start_processing"))
    start_run_generate_key(exc_path, output_directory)
    print(get_localized_text("complete_processing"))
    # 打开执行后的文件夹
    open_folder(output_directory)