import os
import shutil

from localization.localization import get_localized_text
from utils.cache_utils import get_list_use_folder_cache, load_from_cache
from utils.file_utils import find_exc_file, open_folder

def start_run_generate_key(path, dir):
    print()


def run_excel_language_generate_key():
    # 加载缓存
    result = get_list_use_folder_cache(load_from_cache(), "LanguageGenerateKey")
    if not result:
        print(get_localized_text("cancel_choose_tip"))
        return
    exc_path = find_exc_file(result, '.xlsx')

    output_path = os.path.splitext(exc_path)[0]
    output_directory = os.path.join(output_path, "output")
    if os.path.exists(output_directory):
        # 如果文件夹存在删除文件夹
        try:
            shutil.rmtree(output_directory)  # 递归删除文件夹及其内容
        except Exception as e:
            print(get_localized_text("delete_folder_failed", error=str(e)))

    os.makedirs(output_directory)
    # 开始执行操作
    print(get_localized_text("start_processing"))
    start_run_generate_key(exc_path, output_directory)
    print(get_localized_text("complete_processing"))
    # 打开执行后的文件夹
    open_folder(output_directory)