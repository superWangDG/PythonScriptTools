# 使用FFMpeg 格式化媒体
import os
import subprocess
import re
from sysconfig import get_path

from localization.localization import get_localized_text
from utils.cache_utils import load_from_cache, save_to_cache
from utils.file_utils import get_last_folder_name


def run_ffmpeg_medias():
    # 使用视频的文件夹，获取文件内的vep 文件，判断目标是否已经转换，如果没有转换的情况将媒体路径移动到待处理的列表中进行格式转换
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

