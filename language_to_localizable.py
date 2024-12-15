# 使用表格中的多语言文件生成对应系统的应用文件

import pandas as pd
import os
import shutil
import subprocess
import platform
import re

# 开始处理 excel 转为 本地化的语言
def create_files_from_excel(file_path, output_dir):
    # 读取 Excel 文件
    df = pd.read_excel(file_path)
    # 找到 Key 行及之后的内容
    key_row_index = df[df.iloc[:, 0] == "Key"].index[0]
    data_start = key_row_index + 1
    # 得到创建文件的声明
    dir_dict_data = get_dir_data_dict(df.iloc[0:data_start - 1])
    # key 所在的 column 数据
    key_row = df.iloc[key_row_index]
    content_df = df.iloc[data_start:].reset_index(drop=True)
    for key, value in dir_dict_data.items():
        # 判断对应平台是否同时存在 file | folder
        if "file" in value and "folder" in value:
            # 创建文件夹以及得到语言写入的地址
            dir_dict_data[key]["writes"] = create_localizable_dir(key, value, output_dir)

    # 开始遍历表格内容的数据并且生成指定的本地化语言文件
    for idx, row in content_df.iterrows():
        column_key = row.values[0]
        values = row.iloc[1:]
        for r_idx, r_column in enumerate(values):
            for key, value in dir_dict_data.items():
                if key == "iOS":
                    file_path = value["writes"][r_idx]
                    with open(file_path, "a", encoding="utf-8") as f:
                        # 判断 值内的内容是否存在" 并且没有添加转义符号
                        r_column = escape_unescaped_quotes(r_column)
                        r_column = escape_android_unit_to_ios(r_column)
                        # 开始写入数据
                        f.write(f"\"{column_key}\" = \"{r_column}\";\n")


# 使用正则表达式查找并转义未转义的双引号
def escape_unescaped_quotes(text):
    if isinstance(text, str):
        return re.sub(r'(?<!\\)"', r'\\"', text)
    else:
        # 如果不是字符串，返回原始值或其他默认值
        return text


# 将Android 中的通用符号转为iOS中使用的符号
def escape_android_unit_to_ios(text):
    if isinstance(text, str):
        # 替换 %(数字)$s 为 %@
        text = re.sub(r'%\d+\$s', '%@', text)
        # 替换 %(数字)$d 为 %d
        text = re.sub(r'%\d+\$d', '%d', text)
        return text.replace("%s", "%@")
    else:
        # 如果不是字符串，返回原始值或其他默认值
        return text


# 获取文件夹以及文件的数据
def get_dir_data_dict(file_df):
    datalist = {}
    # 创建文件同时创建文件夹
    for idx, row in file_df.iterrows():
        # 增加第一行的信息
        columns = file_df.columns.tolist()
        columns_key = columns[0].split()[0]
        columns_value = columns[0].replace(columns_key, "").strip()
        if "Folder Name" in columns_value:
            # 文件夹的信息
            datalist.setdefault(columns_key, {})["folder"] = columns[1:]
        elif "File Name" in columns_value:
            datalist.setdefault(columns_key, {})["file"] = columns[1:]
        # 增加遍历的信息
        row_key = row.values[0].split()[0]
        row_value = row.values[0].replace(columns_key, "").strip()
        if "Folder Name" in row_value:
            # 文件夹的信息
            datalist.setdefault(row_key, {})["folder"] = row.values[1:]
        elif "File Name" in row_value:
            datalist.setdefault(row_key, {})["file"] = row.values[1:]
    return datalist


# 创建本地化的文件夹, 并返回目标文件的地址
def create_localizable_dir(platform, dict, root_path):
    file_path_list = []
    folder_path = os.path.join(root_path, platform)
    child_list = []
    # 创建子目录
    for key, value in dict.items():
        for idx, item in enumerate(value):
            if key == "folder":
                child_path = os.path.join(folder_path, item)
                os.makedirs(child_path, exist_ok=True)
                child_list.append(child_path)
            elif key == "file":
                file_path_list.append(os.path.join(child_list[idx], item))
    return file_path_list


# 打开生成的根目录
def open_folder(path):
    # 获取当前脚本所在的文件夹路径
    # 根据不同的操作系统选择适当的命令来打开文件夹
    if platform.system() == 'Windows':
        os.startfile(path)  # Windows
    elif platform.system() == 'Darwin':  # macOS
        subprocess.run(['open', path])
    else:  # Linux
        subprocess.run(['xdg-open', path])


# 获取执行excel的目录
def get_excel_folder():
    while True:
        folder_path = input("执行多语言本地化的Excel文件夹路径:\n")
        if os.path.isdir(folder_path):
            exc_file = find_exc_file(folder_path)
            if exc_file:
                return exc_file
        else:
            print("当前输入内容不是文件的目录,请重试")


# 找到需要执行的 Excel 的文件
def find_exc_file(directory):
    """
    在给定目录中查找 .xlsx 文件。
    如果有多个文件，提供选择界面让用户选择要使用的文件。
    """
    xlsx_files = []

    # 遍历目录，收集所有 .xlsx 文件
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".xlsx"):
                xlsx_files.append(os.path.join(root, file))

    if not xlsx_files:
        print("未找到任何 .xlsx 文件。")
        return None

    if len(xlsx_files) == 1:
        print(f"找到一个文件：{xlsx_files[0]}")
        return xlsx_files[0]

    # 多个文件时，让用户选择
    print("找到多个 .xlsx 文件，请选择要使用的文件：")
    for idx, file in enumerate(xlsx_files):
        print(f"{idx + 1}: {file}")

    while True:
        try:
            choice = int(input("请输入文件编号："))
            if 1 <= choice <= len(xlsx_files):
                return xlsx_files[choice - 1]
            else:
                print("输入编号无效，请重新输入。")
        except ValueError:
            print("请输入有效的数字编号。")


# 使用示例
if __name__ == "__main__":
    # excel_path = get_excel_folder()  # 替换为实际路径

    excel_path = "/Users/wang/Downloads/test/result.xlsx"

    # 输出的目录 判断是否存在 output 文件夹，如果没有则创建
    output_directory = os.path.join(os.path.dirname(excel_path), "output")

    if os.path.exists(output_directory):
        # 如果文件夹存在删除文件夹
        try:
            shutil.rmtree(output_directory)  # 递归删除文件夹及其内容
            print(f"文件夹 {output_directory} 及其内容已成功删除")
        except Exception as e:
            print(f"删除文件夹失败: {e}")

    os.makedirs(output_directory)
    # 开始执行操作
    create_files_from_excel(excel_path, output_directory)

    # 打开执行后的文件夹
    # open_folder(output_directory)
