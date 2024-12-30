# ffmpeg -i <URL> -c copy <保存路径>
import os
import subprocess
import re

from localization.localization import get_localized_text
from utils.cache_utils import load_from_cache, save_to_cache
from utils.file_utils import get_last_folder_name, select_source


def get_init_exc_path(orgDict=None):
    path = select_source(file_suffix_list=["json"])
    if not path:
        print(get_localized_text("no_choose_tip"))
        return
    data = {
        "downloadJsonPath": path
    }
    if orgDict is None:
        return data
    # 将新数据合并到 orgDict 中
    orgDict.update(data)
    return orgDict


def get_path(cache_json):
    """获取或选择 Podfile 路径"""
    if not cache_json or not cache_json.get("downloadJsonPath"):
        # 如果没有缓存或 `podfileCommand` 数据缺失
        cache_json = get_init_exc_path(cache_json)
        if not cache_json:
            return None, None  # 用户取消操作
    else:
        excel_path = cache_json["downloadJsonPath"]
        print(get_localized_text("use_last_path", path=excel_path))
        return cache_json, excel_path

    return cache_json, cache_json["downloadJsonPath"]


def run_download_medias():
    cache_json = load_from_cache()
    cache_json, excel_path = get_path(cache_json)
    if not excel_path:
        print(get_localized_text("no_choose_tip"))
        return
    urls_json = load_from_cache(excel_path[0])

    down_path = os.path.join(os.path.expanduser("~"), "Downloads")
    for url in urls_json:
        filename = get_last_folder_name(url)
        save_path = os.path.join(down_path, filename)
        # 构建命令
        command = [
            "ffmpeg",
            "-i", url,
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            save_path,
        ]

        try:
            # 使用 Popen 捕获实时输出
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 实时解析输出
            for line in process.stderr:
                print(line, end="")  # 输出原始日志
                # 提取下载进度
                match = re.search(r"time=(\d{2}:\d{2}:\d{2})", line)
                if match:
                    progress_time = match.group(1)
                    print(f"当前进度: {progress_time}")

            # 等待进程结束
            process.wait()
            if process.returncode == 0:
                print(f"下载完成: {filename}")
            else:
                print(f"下载失败，返回码: {process.returncode}")
        except Exception as e:
            print(f"执行命令时出错: {e}")

    save_to_cache(urls_json)


# 等级低于20级想要获取资源游戏主页右上角点击【活动】【新友召集令】绑定邀请码07-46-BV-BT-DI即可领取。各种兑换码送给欧皇的各位新手朋友兑换码   kaifu888  cx666    cx888   cx999  ty666  zb8w8 xls666  kaifu666  qingdian666  qingdian333  alw66 swz999 qingdian333 alw66 dasheng666 qitian888 happy2025长按复制即可