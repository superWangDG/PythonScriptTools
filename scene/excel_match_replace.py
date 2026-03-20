import os
import shutil
import pandas as pd

from localization.localization import get_localized_text
from utils.cache_utils import load_from_cache, get_list_use_folder_cache
from utils.file_utils import find_exc_file, open_folder


def start_match_to_replace(path, dir):
    print(f"地址: {path}, 目录: {dir}")
    # 读取 Excel 文件
    df_default = pd.read_excel(path, sheet_name="translate")  # 默认 sheet

    # 读取默认 sheet 第一行的 sheet 名称（排除第一个 'English'）
    target_sheets = df_default.columns[1:].tolist()

    # 读取所有目标 sheet 数据
    sheets_data = pd.read_excel(path, sheet_name=target_sheets)

    # 遍历每个目标 sheet
    for sheet_name in target_sheets:
        df_target = sheets_data[sheet_name]  # 读取该 sheet 数据
        mapping = {}

        # 遍历 target sheet，每 3 行解析一次
        for i in range(0, len(df_target) - 2, 3):  # 每个数据块间隔 2 行
                # break  # 避免索引越界
            english_names = df_target.iloc[i, 0:].dropna().values  # 第一行是英文
            translated_values = df_target.iloc[i + 2, 0:].dropna().values  # 第二行是目标语言的翻译

            for eng, translated in zip(english_names, translated_values):
                mapping[str(eng).strip()] = str(translated).strip()  # 去除多余空格

        # 匹配并填充默认 sheet 的对应列
        df_default[sheet_name] = df_default["English"].map(mapping)

    # 保存修改后的 Excel 文件
    df_default.to_excel(os.path.join(dir, "updated_file.xlsx"), index=False)


# 使用示例
def run_excel_match_to_replace():
    # 加载缓存
    result = get_list_use_folder_cache(load_from_cache(), "ExcelMatchReplace")
    if not result:
        print(get_localized_text("cancel_choose_tip"))
        return
    exc_path = find_exc_file(result, '.xlsx')

    output_path = os.path.splitext(exc_path)[0]
    print(f"result: {output_path}")
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
    start_match_to_replace(exc_path, output_directory)
    print(get_localized_text("complete_processing"))
    # 打开执行后的文件夹
    open_folder(output_directory)