
import platform
import os
import subprocess
import tkinter as tk
from tkinter import filedialog

from localization.localization import get_localized_text


# 选择资源 only_folder 为False时可以设置 file_suffix_list 限定文件的类型
def select_source(title=get_localized_text("choose_file"), only_folder=False, file_suffix_list=[]):
    # 创建一个隐藏的根窗口
    root = tk.Tk()
    # 隐藏根窗口
    root.withdraw()
    # 获取桌面路径
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    if only_folder is True:
        return filedialog.askdirectory(title=title, initialdir=desktop_path)
    else:
        # 选择文件，并限制文件类型
        filetypes = []
        for suffix in file_suffix_list:
            filetypes.append((f"{suffix} files", f"*.{suffix}"))
        # 弹出文件选择框，允许选择多个文件
        file_paths = filedialog.askopenfilenames(
            title=title,
            filetypes=filetypes
        )
        return file_paths


# 找到指定文件夹内是否有满足指定条件的文件
def find_folders_with_files(folder_path, file_names=None, file_suffixes=None):
    """
    查询选中的文件夹及其子文件夹中是否包含指定文件名或指定后缀类型的文件

    :param folder_path: 要查询的根文件夹路径
    :param file_names: 完全匹配的文件名列表
    :param file_suffixes: 后缀匹配的文件类型列表（如 '.txt', '.json'）
    :return: 包含目标文件或类型的文件夹路径列表
    """
    matching_folders = []
    # 遍历选中文件夹及其子文件夹
    for root, dirs, files in os.walk(folder_path):
        # 检查是否包含完全匹配的文件
        has_target_file = file_names and any(file in files for file in file_names)
        # 检查是否包含指定后缀的文件
        has_target_suffix = file_suffixes and any(file.endswith(tuple(file_suffixes)) for file in files)
        # 如果满足任一条件，将文件夹路径加入结果
        if has_target_file or has_target_suffix:
            matching_folders.append(root)

    return matching_folders


def get_last_folder_name(path):
    """从路径中提取最后一级文件夹名称"""
    return os.path.basename(path.rstrip(os.sep))


# 获取执行的目录
def get_execute_folder(file_suffix=".xlsx"):
    while True:
        folder_path = input(get_localized_text("input_execute_folder_tip", suffix=file_suffix)).strip()
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
