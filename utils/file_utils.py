
import platform
import os
import subprocess

from localization.localization import get_localized_text


# 获取执行的目录
def get_execute_folder(file_suffix=".xlsx"):
    while True:
        folder_path = input(get_localized_text("input_execute_folder_tip")).strip()
        if os.path.isdir(folder_path):
            exc_file = find_exc_file(folder_path, file_suffix)
            if exc_file:
                return exc_file
        else:
            print(get_localized_text("this_path_not_folder"))


# 找到需要执行的 Excel 的文件
def find_exc_file(directory, file_suffix):
    """
    在给定目录中查找 .xlsx 文件。
    如果有多个文件，提供选择界面让用户选择要使用的文件。
    """
    match_files = []
    # 遍历目录，收集所有 .xlsx 文件
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(file_suffix):
                match_files.append(os.path.join(root, file))

    if not match_files:
        print(get_localized_text("file_not_found", suffix=file_suffix))
        return None

    # 只有一个文件的情况下直接返回
    if len(match_files) == 1:
        return match_files[0]

    # 多个文件时，让用户选择
    print(get_localized_text("find_multiple_files", suffix=file_suffix))

    for idx, file in enumerate(match_files):
        print(f"{idx + 1}: {file}")
    while True:
        try:
            choice = int(input(get_localized_text("please_input_file_no")))
            if 1 <= choice <= len(match_files):
                return match_files[choice - 1]
            else:
                print(get_localized_text("invalid_number"))
        except ValueError:
            print(get_localized_text("enter_valid_number"))


# 打开生成的根目录
def open_folder(path):
    # 根据不同的操作系统选择适当的命令来打开文件夹
    if platform.system() == 'Windows':
        os.startfile(path)  # Windows
    elif platform.system() == 'Darwin':  # macOS
        subprocess.run(['open', path])
    else:  # Linux
        subprocess.run(['xdg-open', path])
