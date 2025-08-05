# 自动下载节假日的JSON 文件并存储本地

import os
import platform
import json
import hashlib
import time
from typing import Optional

import requests
import zipfile
from datetime import datetime

from utils.file_utils import open_folder


def get_current_year() -> int:
    """返回当前年份"""
    return datetime.now().year


def get_download_dir(subfolder: str = "HolidayJSON") -> str:
    """返回平台默认下载目录下的指定子目录路径"""
    system = platform.system()
    if system == "Windows":
        base_path = os.path.join(os.environ["USERPROFILE"], "Downloads")
    elif system == "Darwin":
        base_path = os.path.join(os.environ["HOME"], "Downloads")
    else:
        raise OSError(f"Unsupported OS: {system}")

    target_dir = os.path.join(base_path, subfolder)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def json_file_exists(path: str, content_hash: str = None) -> bool:
    """判断文件是否存在，如传入 hash 则对比内容"""
    if not os.path.exists(path):
        return False
    if content_hash:
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_hash = hashlib.md5(json.dumps(existing_data, sort_keys=True).encode()).hexdigest()
            return existing_hash == content_hash
        except Exception:
            return False
    return True


def compress_to_zip(folder_path: str) -> str:
    """将指定文件夹内所有 .json 文件压缩为 holidays.zip，返回压缩后的路径"""
    zip_path = os.path.join(folder_path, "holidays.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(folder_path, file_name)
                zipf.write(file_path, arcname=file_name)

    print(f"已将所有 JSON 压缩为：{zip_path}")
    return zip_path


def download_json_if_needed(json_data: dict, filename: str):
    """保存 JSON 文件到本地，并压缩为 zip"""
    target_dir = get_download_dir("HolidayJSON")
    save_path = os.path.join(target_dir, filename)

    content_hash = hashlib.md5(json.dumps(json_data, sort_keys=True).encode()).hexdigest()

    if json_file_exists(save_path, content_hash):
        print("文件已存在且内容一致，跳过下载。")
    else:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"已保存 JSON 到：{save_path}")

            # 阻塞 60 秒
    print("等待 30 秒避免拦截后继续...")
    time.sleep(30)

def get_browser_headers() -> dict:
    """返回模拟浏览器请求的 headers"""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",  # 请求压缩响应
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "http://timor.tech/",
        "Origin": "http://timor.tech",
        # "Cookie": "xxx=xxx",  # 如果接口需要登录状态，可补充
        # 其他头视情况添加
    }


def fetch_holiday_data_for_year(year: int) -> Optional[dict]:
    """请求 holiday 数据，若无 holiday 字段或为空，则返回 None"""
    # url = f"https://example.com/api/holidays/{year}"  # ← 你替换为真实 URL
    url = f"http://timor.tech/api/holiday/year/{year}/"
    print(f"请求接口：{url}")
    response = requests.get(url, headers=get_browser_headers())
    if response.status_code != 200:
        raise Exception(f"请求失败：{response.status_code}")

    data = response.json()

    if not isinstance(data, dict):
        print(f"[警告] 返回数据不是 dict 类型（year: {year}），终止处理。")
        return None
    # 检查 holiday 字段
    holiday_data = data.get("holiday")
    if not holiday_data:
        print(f"无假期数据（year: {year}），终止处理。")
        return None

    return data


# 开始运行自动下载节假日的文件
def run_recursive_download():
    """从当前年份开始，向前逐年下载 holiday 数据，直到 holiday 字段为空为止"""
    year = get_current_year()
    min_year = 2010

    target_dir = get_download_dir("HolidayJSON")

    while year >= min_year:
        file_name = f"holiday_{year}.json"
        saved_path = os.path.join(target_dir, file_name)

        # 如果本地已存在文件，跳过
        if os.path.exists(saved_path):
            print(f"{file_name} 已存在，跳过。")
            year -= 1
            continue

        # 请求接口数据
        json_data = fetch_holiday_data_for_year(year)

        if not json_data:
            print(f"未能获取 {year} 年的数据，终止。")
            break

        # 校验 holiday 字段是否存在并非空
        holiday_data = json_data.get("holiday")
        if not holiday_data:
            print(f"{year} 年的 holiday 字段为空，终止。")
            break

        # 下载并保存文件，如果成功则内部会等待 60 秒
        download_json_if_needed(json_data, file_name)

        # 继续前一年
        year -= 1

    # 压缩下载文件夹
    compress_to_zip(target_dir)

    # 打开文件夹
    open_folder(target_dir)

    print("所有任务完成。")


# === 测试代码 ===
# if __name__ == "__main__":
#     current_year = get_current_year()
#     json_data = fetch_holiday_data_for_year(current_year)
#
#     if json_data:
#         file_name = f"holiday_{current_year}.json"
#         download_json_if_needed(json_data, file_name)