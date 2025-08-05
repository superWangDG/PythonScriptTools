import os
import platform
import json
import hashlib
import time
from typing import Optional, List

import requests
import zipfile
from datetime import datetime

from utils.file_utils import open_folder

# 全局属性：支持的国家/地区列表
COUNTRIES = ["CN", "US", "GB", "DE", "FR", "JP"]  # 可以根据需要添加更多国家


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


def get_country_dir(country: str, base_dir: str) -> str:
    """为指定国家创建子目录"""
    country_dir = os.path.join(base_dir, country)
    os.makedirs(country_dir, exist_ok=True)
    return country_dir


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
    """将整个 HolidayJSON 文件夹压缩为 holidays.zip，包含所有国家子目录"""
    zip_path = os.path.join(folder_path, "holidays.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    # 计算相对路径，保持目录结构
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname=arcname)

    print(f"已将所有国家的 JSON 文件压缩为：{zip_path}")
    return zip_path


def download_json_if_needed(json_data: dict, filename: str, country_dir: str):
    """保存 JSON 文件到指定国家目录"""
    save_path = os.path.join(country_dir, filename)

    content_hash = hashlib.md5(json.dumps(json_data, sort_keys=True).encode()).hexdigest()

    if json_file_exists(save_path, content_hash):
        print(f"文件 {filename} 已存在且内容一致，跳过下载。")
    else:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"已保存 JSON 到：{save_path}")

    # 等待 30 秒避免请求过于频繁
    print("等待 10 秒避免拦截后继续...")
    time.sleep(10)


def get_browser_headers() -> dict:
    """返回模拟浏览器请求的 headers"""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "http://timor.tech/",
        "Origin": "http://timor.tech",
    }


def fetch_cn_holiday_data_for_year(year: int) -> Optional[dict]:
    """请求中国 holiday 数据，若无 holiday 字段或为空，则返回 None"""
    url = f"http://timor.tech/api/holiday/year/{year}/"
    print(f"请求中国接口：{url}")

    try:
        response = requests.get(url, headers=get_browser_headers(), timeout=30)
        if response.status_code != 200:
            print(f"请求失败：{response.status_code}")
            return None

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
    except Exception as e:
        print(f"请求中国API出错: {e}")
        return None


def fetch_other_country_holiday_data(country: str, year: int) -> Optional[dict]:
    """请求其他国家的 holiday 数据"""
    url = f"https://date.nager.at/api/v3/publicholidays/{year}/{country}"
    print(f"请求 {country} 接口：{url}")

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"请求失败：{response.status_code}")
            return None

        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            print(f"[警告] {country} {year} 年无假期数据")
            return None

        return {"holidays": data, "country": country, "year": year}
    except Exception as e:
        print(f"请求 {country} API出错: {e}")
        return None


def download_country_holidays(country: str, target_dir: str):
    """下载指定国家的节假日数据"""
    print(f"\n开始下载 {country} 的节假日数据...")

    country_dir = get_country_dir(country, target_dir)
    year = get_current_year()

    # 如果国家不是中国的获取往后10年的数据
    if country != "CN":
        year += 10

    min_year = 2010

    while year >= min_year:
        file_name = f"holiday_{year}.json"
        saved_path = os.path.join(country_dir, file_name)

        # 如果本地已存在文件，跳过
        if os.path.exists(saved_path):
            print(f"{country} - {file_name} 已存在，跳过。")
            year -= 1
            continue

        # 根据国家选择不同的API
        if country == "CN":
            json_data = fetch_cn_holiday_data_for_year(year)

            if not json_data:
                print(f"未能获取 {country} {year} 年的数据，终止。")
                break

            # 校验 holiday 字段是否存在并非空
            holiday_data = json_data.get("holiday")
            if not holiday_data:
                print(f"{country} {year} 年的 holiday 字段为空，终止。")
                break
        else:
            json_data = fetch_other_country_holiday_data(country, year)

            if not json_data:
                print(f"未能获取 {country} {year} 年的数据，终止。")
                break

        # 下载并保存文件
        download_json_if_needed(json_data, file_name, country_dir)

        # 继续前一年
        year -= 1

    print(f"{country} 的数据下载完成。")


def run_recursive_download():
    """下载所有配置国家的节假日数据"""
    target_dir = get_download_dir("HolidayJSON")

    print(f"开始下载以下国家的节假日数据: {', '.join(COUNTRIES)}")

    for country in COUNTRIES:
        try:
            download_country_holidays(country, target_dir)
        except Exception as e:
            print(f"下载 {country} 数据时出错: {e}")
            continue

    # 压缩整个 HolidayJSON 文件夹
    compress_to_zip(target_dir)

    # 打开文件夹
    open_folder(target_dir)

    print("所有任务完成。")


if __name__ == "__main__":
    run_recursive_download()