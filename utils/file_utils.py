import platform
import os
import subprocess

from localization.localization import get_localized_text


# ─── 文件/文件夹选择 ──────────────────────────────────────────────────────────

def _select_folder_macos(title: str) -> str:
    """macOS 使用 osascript 弹出文件夹选择框，完全绕开 tkinter。"""
    script = f'tell application "Finder" to set p to POSIX path of (choose folder with prompt "{title}")'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True
    )
    path = result.stdout.strip()
    return path if path else ""


def _select_files_macos(title: str, file_suffix_list: list) -> tuple:
    """macOS 使用 osascript 弹出多文件选择框。"""
    if file_suffix_list:
        type_filter = "{" + ", ".join(f'"{s}"' for s in file_suffix_list) + "}"
        script = (
            f'tell application "Finder" to set fs to '
            f'(choose file with prompt "{title}" of type {type_filter} with multiple selections allowed)\n'
            f'set output to ""\n'
            f'repeat with f in fs\n'
            f'  set output to output & POSIX path of f & "\\n"\n'
            f'end repeat\n'
            f'output'
        )
    else:
        script = (
            f'tell application "Finder" to set fs to '
            f'(choose file with prompt "{title}" with multiple selections allowed)\n'
            f'set output to ""\n'
            f'repeat with f in fs\n'
            f'  set output to output & POSIX path of f & "\\n"\n'
            f'end repeat\n'
            f'output'
        )
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True
    )
    paths = [p for p in result.stdout.strip().splitlines() if p]
    return tuple(paths)


def _select_folder_tkinter(title: str) -> str:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    path = filedialog.askdirectory(title=title, initialdir=desktop_path)
    root.destroy()
    return path


def _select_files_tkinter(title: str, file_suffix_list: list) -> tuple:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    filetypes = [(f"{s} files", f"*.{s}") for s in file_suffix_list]
    paths = filedialog.askopenfilenames(title=title, filetypes=filetypes)
    root.destroy()
    return paths


# 选择资源 only_folder 为 False 时可以设置 file_suffix_list 限定文件类型
def select_source(title=get_localized_text("choose_file"), only_folder=False, file_suffix_list=[]):
    is_mac = platform.system() == "Darwin"

    if only_folder:
        if is_mac:
            return _select_folder_macos(title)
        else:
            return _select_folder_tkinter(title)
    else:
        if is_mac:
            return _select_files_macos(title, file_suffix_list)
        else:
            return _select_files_tkinter(title, file_suffix_list)


# ─── 文件夹工具 ───────────────────────────────────────────────────────────────

def find_folders_with_files(folder_path, file_names=None, file_suffixes=None):
    """
    查询选中的文件夹及其子文件夹中是否包含指定文件名或指定后缀类型的文件。

    :param folder_path: 要查询的根文件夹路径
    :param file_names: 完全匹配的文件名列表
    :param file_suffixes: 后缀匹配的文件类型列表（如 '.txt', '.json'）
    :return: 包含目标文件或类型的文件夹路径列表
    """
    matching_folders = []
    for root, dirs, files in os.walk(folder_path):
        has_target_file = file_names and any(file in files for file in file_names)
        has_target_suffix = file_suffixes and any(file.endswith(tuple(file_suffixes)) for file in files)
        if has_target_file or has_target_suffix:
            matching_folders.append(root)
    return matching_folders


def get_last_folder_name(path):
    """从路径中提取最后一级文件夹名称"""
    return os.path.basename(path.rstrip(os.sep))


def get_execute_folder(file_suffix=".xlsx"):
    while True:
        folder_path = input(get_localized_text("input_execute_folder_tip", suffix=file_suffix)).strip()
        if os.path.isdir(folder_path):
            exc_file = find_exc_file(folder_path, file_suffix)
            if exc_file:
                return exc_file
        else:
            print(get_localized_text("this_path_not_folder"))


def find_exc_file(directory, file_suffix):
    """
    在给定目录中查找指定后缀文件。
    如果有多个文件，提供选择界面让用户选择。
    """
    match_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(file_suffix):
                match_files.append(os.path.join(root, file))

    if not match_files:
        print(get_localized_text("file_not_found", suffix=file_suffix))
        return None

    if len(match_files) == 1:
        return match_files[0]

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


def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])