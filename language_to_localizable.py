# 使用表格中的多语言文件生成对应系统的应用文件

import pandas as pd
import os
import subprocess
import platform


class ConfigMainModel:
    def __init__(self, platform, item):
        self.platform = platform
        self.item = item


class ConfigItemModel:
    def __init__(self, folderName, fileName):
        self.folderName = folderName
        self.fileName = fileName


def create_files_from_excel(file_path, output_dir):
    """
    根据 Excel 内容生成 Android 和 iOS 的文件结构和内容。

    :param file_path: 输入的 Excel 文件路径
    :param output_dir: 生成文件的根目录
    """
    print(f"读取文件: {file_path}")
    # 读取 Excel 文件
    df = pd.read_excel(file_path)

    # 找到 Key 行及之后的内容
    key_row_index = df[df.iloc[:, 0] == "Key"].index[0]
    data_start = key_row_index + 1

    # 是否生成 iOS 的本地化文件
    generate_ios = False
    # 是否生成 Android 的本地化文件
    generate_android = False
    # 得到创建文件的声明
    dir_dict_data = get_dir_data_dict(df.iloc[0:data_start - 1])
    # print(f"输出文件夹的声明: {file_df}")
    #
    # key 所在的 column 数据
    key_row = df.iloc[key_row_index]
    content_df = df.iloc[data_start:].reset_index(drop=True)
    for key, value in dir_dict_data.items():
        print(f"遍历数据: key: {key} , value{value} , key row: {key_row}")


        # 表格的第一行
        # first_row = file_df.columns.tolist()
        # if first_row[0].find("Android") != -1 and row.iloc[0].find("Android") != -1:
        #     generate_android = True
        #     folder_path = os.path.join(output_dir, "Android")
        #     create_localizable_dir(first_row, row, folder_path)
        #
        # elif first_row[0].find("iOS") != -1 and row.iloc[0].find("iOS") != -1:
        #     generate_ios = True
        #     folder_path = os.path.join(output_dir, "iOS")
        #     create_localizable_dir(first_row, row, folder_path)
        # else:
        #     # 判断是创建 文件夹还是 文件
        #     print(f"遍历其他的情况")




        # os.makedirs(folder_path, exist_ok=True)
        # file_path = os.path.join(folder_path, file_name)
    # for idx, row in content_df.iterrows():
        # if idx == 0:
            # print(f"当前输出的第一行的数据: {row}")

    # for platform, config in platforms.items():
    #     folder_col = config["folder_col"]
    #     file_col = config["file_col"]
    #     base_dir = config["base_dir"]
    #
    #     print(f"输出平台 {folder_col}  / file {folder_col} / basedir {base_dir}")
        # 遍历每一行，生成文件夹和文件
        # for _, row in content_df.iterrows():

            # print(f"输出Row {row}")
            # folder_name = row[folder_col]
            # file_name = row[file_col]


            # if not pd.notna(folder_name) or not pd.notna(file_name):
            #     continue  # 跳过无效行
            #
            # # 构造完整路径
            # folder_path = os.path.join(base_dir, folder_name)
            # os.makedirs(folder_path, exist_ok=True)
            # file_path = os.path.join(folder_path, file_name)
            #
            # # 写入文件内容
            # with open(file_path, "w", encoding="utf-8") as f:
            #     for lang, value in row.items():
            #         if lang in key_row.values and pd.notna(value):
            #             key = row["Key"]
            #             f.write(f"{key} = {value}\n")
            #
            # print(f"[{platform}] 文件生成: {file_path}")


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
def create_localizable_dir(first_row, row, folder_path):
    file_path_list = []
    # 生成子目录(判断column 是文件夹还是文件)
    folder_data_source = first_row if first_row and "Folder Name" in first_row[0] else row.columns.tolist()
    # 移除第一个字符串
    folder_data_source = folder_data_source[1:]
    file_data_source = first_row if first_row and "File Name" in first_row[0] else row.values
    file_data_source = file_data_source[1:]
    # 创建子目录
    for item_idx, value in enumerate(folder_data_source):
        child_path = os.path.join(folder_path, value)
        os.makedirs(child_path, exist_ok=True)
        file_path_list.append(os.path.join(child_path, file_data_source[item_idx]))
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

    excel_path = "/Users/apple/Downloads/替换/result.xlsx"

    # 输出的目录 判断是否存在 output 文件夹，如果没有则创建
    output_directory = os.path.join(os.path.dirname(excel_path), "output")

    if not os.path.exists(output_directory):
        # 不存在文件夹创建了文件夹
        os.makedirs(output_directory)

    # 开始执行操作
    create_files_from_excel(excel_path, output_directory)

    # 打开执行后的文件夹
    open_folder(output_directory)
