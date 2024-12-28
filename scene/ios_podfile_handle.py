# 执行Cocoapods 的指令（）
import os
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


def run_podfile_handle():
    # 得到执行的路径(如果有缓存的情况下读取缓存)
    excel_path = select_source(only_folder=True)
    if not excel_path:
        print(get_localized_text("no_choose_tip"))
        return
    # 遍历得到选中文件夹中含有Podfile文件的项目文件夹
    match_path = find_folders_with_files(folder_path=excel_path, file_names=["Podfile"])
    print(get_localized_text("please_project_tip"))
    for (index, item) in enumerate(match_path):
        tip = get_localized_text("please_project_item", name=get_last_folder_name(item), num=index + 1)
        print(f"{tip}")

    get_path = input_project_number(match_path)
    if not get_path:
        print(get_localized_text("no_choose_tip"))
        return
    command_list = [
        'pod install',
        'pod update',
        'pod install --no-repo-update',
        'pod update --no-repo-update'
    ]

    for (index, item) in enumerate(command_list):
        print(get_localized_text("execution_operations", command=item, num=index + 1))

    get_command = input_project_number(command_list)
    if not get_command:
        print(get_localized_text("no_choose_tip"))
        return

    # 开始执行指令
    exc_command = f"cd '{get_path}' && {get_command}"
    print(f"开始执行指令: {exc_command}")
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
