# ffmpeg -i <URL> -c copy <保存路径>
import os
import subprocess
import re
from utils.file_utils import get_last_folder_name


def run_download_medias():
    urls = [
        # "https://dow6.lzidw.com/20240108/33563_81e04ede/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-01.mp4",
        "https://dow6.lzidw.com/20240114/33751_62aec794/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-02.mp4",
        # "https://dow6.lzidw.com/20240121/33994_d910999e/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-03.mp4",
        # "https://dow6.lzidw.com/20240129/34221_2385556a/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-04.mp4",
        # "https://dow6.lzidw.com/20240205/34479_8f8f8476/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-05.mp4",
        # "https://dow6.lzidw.com/20240212/34716_68533830/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-06.mp4",
        # "https://dow.dowlz6.com/20240219/34957_ae7b0df2/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-07.mp4",
        # "https://dow.dowlz6.com/20240226/35223_5c2a52b7/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-08.mp4",
        # "https://dow.dowlz6.com/20240304/35439_6d355cb3/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-09.mp4",
        # "https://dow.dowlz6.com/20240310/35711_73a3a763/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-10.mp4",
        # "https://dow.dowlz6.com/20240318/36008_94f37e58/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-11.mp4",
        # "https://dow.dowlz6.com/20240324/36314_d2cdc1b6/因为不是真正的伙伴而被逐出勇者队伍，流落到边境展开慢活人生第二季-12.mp4"
    ]



    down_path = os.path.join(os.path.expanduser("~"), "Downloads")
    for url in urls:
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
