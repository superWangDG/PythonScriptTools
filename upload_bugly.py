import subprocess
import os
import re
"""
这是一个bugly 上传 dYSM 文件的脚本
"""


class ConfigModel:
    def __init__(self, appid, appKey, bundleId, version=None, jarFilePath=None, sourcePath=None):
        self.appid = appid
        self.appKey = appKey
        self.bundleId = bundleId
        self.version = version  # 默认值为 None
        self.jarFilePath = jarFilePath
        self.sourcePath = sourcePath


# 使用示例
config = ConfigModel(
    appid="7cb36de15a",
    appKey="04fbbba5-4271-4fd6-a0b9-4cfab83e9bb7",
    bundleId="com.cloudhearing.ios.ClickFree",
)


def list_files_in_current_directory():
    # 获取当前脚本所在目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # print(f"当前目录: {current_directory}\n")
    # 列出当前目录中的所有文件和文件夹
    files_and_folders = os.listdir(current_directory)
    for item in files_and_folders:
        item_path = os.path.join(current_directory, item)
        if item == 'buglyqq-upload-symbol.jar':
            config.jarFilePath = item_path
            continue
        if os.path.isfile(item_path):
            if item.endswith(".dSYM"):
                # 如果当前目录存在 dSYM 文件的情况直接使用当前的目录
                config.sourcePath = current_directory
        elif os.path.isdir(item_path):
            # 检查目录中是否包含 .dSYM 文件
            if not config.sourcePath:
                dsym_directory = find_dsym_in_directory(item_path)
                # print(f"遍历目录的结果：{dsym_directory}, 从目录中开始查找：{item_path}")
                if dsym_directory:
                    config.sourcePath = current_directory

    if not config.jarFilePath:
        config.jarFilePath = get_valid_jar_path()

    if not config.sourcePath:
        config.sourcePath = get_valid_dsym_upload_folder()

    if not config.version:
        config.version = get_version_string()


# 校验是否为版本号
def is_valid_number(input_string):
    pattern = r'^\d+(\.\d+)+$'
    if re.match(pattern, input_string):
        return True
    return False


def get_version_string():
    while True:
        version = input("请输入当前上传的版本:\n")
        if is_valid_number(version):
            return version
        else:
            print(f"请输入正确的版本号input: {version}")


def get_valid_jar_path():
    """
    获取有效的 jar 文件路径，若路径无效，要求用户重新输入
    """
    while True:
        jar_path = input("未找到 jar 包，请输入 buglyqq-upload-symbol.jar 的路径:\n")
        if jar_path.endswith(".jar") and os.path.isfile(jar_path):
            return jar_path
        else:
            print("输入的文件路径无效，请确认路径是否正确。")


def get_valid_dsym_upload_folder():
    while True:
        folder_path = input("未找到 dYSM 文件的目录 请手动输入 dYSM 的路径:\n")
        if os.path.isdir(folder_path):
            """判断当前文件是否得到dYSM 文件的目录"""
            dsym_directory = find_dsym_in_directory(folder_path)
            if dsym_directory:
                return dsym_directory
        else:
            print("当前输入内容不是文件的目录,请重试")


def find_dsym_in_directory(directory):
    """
    在给定目录中查找 .dSYM 文件，如果找到则返回包含 .dSYM 文件的目录路径。
    """
    for root, children, files in os.walk(directory):
        # 当前根目录的
        for child in children:
            if child.endswith(".dSYM"):
                return root

        for file in files:
            if file.endswith(".dSYM"):
                return root  # 返回找到的 .dSYM 文件所在的目录路径
    return None


# 扫描当前的目录并设置 jar包的地址以及 上传文件的目录 上传的版本
list_files_in_current_directory()

# 构建命令
command = [
    "java",
    "-jar",
    config.jarFilePath,
    "-appid", config.appid,
    "-appkey", config.appKey,
    "-bundleid", config.bundleId,
    "-version", config.version,
    "-platform", 'IOS',
    "-inputSymbol", config.sourcePath
]

try:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(f"命令执行完成，返回码: {result.returncode}")
    print(f"输出: {result.stdout}")
    print(f"错误信息: {result.stderr}" if result.stderr else "无错误信息")
except Exception as e:
    print(f"执行命令时出错: {e}")

