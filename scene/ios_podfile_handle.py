# 执行Cocoapods 的指令（）
import os

from utils.cache_utils import load_from_cache, save_to_cache
from utils.file_utils import select_source, find_folders_with_files, get_last_folder_name
from localization.localization import get_localized_text


def input_project_number(source_list):
    # 获取输入编号后的项目地址
    while True:
        input_content = input(get_localized_text("please_project_tip")).strip()
        if input_content == "exit":
            return
        try:
            if int(input_content) >= len(source_list):
                print(get_localized_text("please_valid_number"))
            else:
                # 满足条件
                return source_list[int(input_content) - 1]
        except ValueError:
            print(get_localized_text("please_valid_number"))


def get_init_exc_path(orgDict=None):
    excel_path = select_source(only_folder=True)
    if not excel_path:
        print(get_localized_text("no_choose_tip"))
        return
    data = {
        "podfileCommand": {
            "path": excel_path,
            "command": None
        }
    }
    if orgDict is None:
        return data
    # 将新数据合并到 orgDict 中
    orgDict.update(data)
    return orgDict


def get_podfile_path(cache_json):
    """获取或选择 Podfile 路径"""
    if not cache_json or not cache_json.get("podfileCommand"):
        # 如果没有缓存或 `podfileCommand` 数据缺失
        cache_json = get_init_exc_path(cache_json)
        if not cache_json:
            return None, None  # 用户取消操作
    else:
        excel_path = cache_json["podfileCommand"]["path"]
        print(get_localized_text("use_last_path", path=excel_path))
        return cache_json, excel_path

    return cache_json, cache_json["podfileCommand"]["path"]


def choose_command(cache_json):
    """获取或选择执行命令"""
    if cache_json["podfileCommand"].get("command"):
        # 如果有缓存的命令
        command = cache_json["podfileCommand"]["command"]
        print(get_localized_text("use_last_command", command=command))
        return command

    # 无缓存，手动选择
    command_list = [
        'pod install',
        'pod update',
        'pod install --no-repo-update',
        'pod update --no-repo-update'
    ]
    for index, cmd in enumerate(command_list):
        print(get_localized_text("execution_operations", command=cmd, num=index + 1))

    command = input_project_number(command_list)
    if not command:
        print(get_localized_text("no_choose_tip"))
        return None
    cache_json["podfileCommand"]["command"] = command
    return command


def run_podfile_handle():
    """主逻辑"""
    # 加载缓存
    cache_json = load_from_cache()

    # 获取 Podfile 路径
    cache_json, excel_path = get_podfile_path(cache_json)
    if not excel_path:
        print(get_localized_text("no_choose_tip"))
        return

    # 找到含 Podfile 的项目文件夹
    match_path = find_folders_with_files(folder_path=excel_path, file_names=["Podfile"])
    if not match_path:
        print(get_localized_text("no_podfile_found"))
        return

    print(get_localized_text("please_project_tip"))
    for index, item in enumerate(match_path):
        tip = get_localized_text("please_project_item", name=get_last_folder_name(item), num=index + 1)
        print(tip)

    get_path = input_project_number(match_path)
    if not get_path:
        print(get_localized_text("no_choose_tip"))
        return

    # 获取或选择执行命令
    get_command = choose_command(cache_json)
    if not get_command:
        return

    # 存储缓存
    save_to_cache(cache_json)

    # 执行指令
    exc_command = f"cd '{get_path}' && {get_command}"
    os.system(exc_command)

    # pod --version # 检查 CocoaPods 是否安装成功及其版本号
    # pod repo update #更新本地库
    # pod init #创建默认的 Podfile
    # pod install # 安装 CocoaPods 的配置文件 Podfile
    # pod install --no-repo-update # 安装框架，不更新本地索引，速度快，但是不会升级本地代码库
    # pod update 升级、添加、删除框架
    # pod update --no-repo-update #安装新框架或者删除不用的框架，但是不会升级项目已经安装的框架
    # pod search AFNetworking #搜索框架
    # pod cache list #查看缓存
