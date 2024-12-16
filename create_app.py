# 用于打包 python 应用
import os
import subprocess
from utils.file_utils import get_execute_folder, open_folder


def execute_command(file_path, file_name):
    # 构建命令
    package_command = [
        "pyinstaller",
        "--onefile",
        "--add-data", "localization/localization.json:localization"
        "--windowed",
        "--name", file_name,
        "--distpath", os.path.join(os.path.dirname(file_path), "output"),
        file_path
    ]

    package_clear_build = [
        "rm",
        "-r", os.path.join(os.path.dirname(file_path), "build"),
    ]
    package_clear_spec = [
        "rm",
        os.path.join(os.path.dirname(file_path), file_name+".spec"),
    ]
    try:
        result = subprocess.run(package_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"--------------打包完成Code: {result.returncode}-------------------")
        # print(f"输出: {result.stdout}")
        subprocess.run(package_clear_build, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        subprocess.run(package_clear_spec, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        open_folder(os.path.join(os.path.dirname(file_path), "output"))
    except Exception as e:
        print(f"执行命令时出错: {e}")


if __name__ == "__main__":
    excel_path = get_execute_folder(".py")  # 替换为实际路径
    package_name = input("请输入应用的名称:\n")
    print("--------------开始执行打包操作-------------------")
    execute_command(excel_path, package_name)
