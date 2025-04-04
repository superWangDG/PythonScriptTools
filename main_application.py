from scene.excel_match_replace import run_excel_match_to_replace
from scene.ffmpeg_source_code_to_lib import run_ffmpeg_make
from scene.ios_podfile_handle import run_podfile_handle
from scene.reset_cache import reset_cache
from scene.strings_replace import run_strings_replace
from scene.upload_bugly import run_update_bugly
from scene.language_to_localizable import run_exc_lang_to_localizable_files
from scene.excel_orgifile_match_replace import run_exc_org_match_rep
from scene.ffmpeg_donwload_files import run_download_medias


def running():
    # 执行功能分选
    funcs = [
        "1.Bugly 符号表上传",
        "2.excel 文件开发多语言生成",
        "3.excel 指定的语言文本匹配替换",
        "4.执行iOS项目Cocoapods 的管理操作",
        "5.使用ffmpeg 下载媒体",
        "6.iOS多语言文件Value值使用替换的规则替换数据",
        "7.使用PY编译FFMpeg",
        "8.重置缓存",
        "9.将多个表格的内容进行匹配替换"
    ]
    print("请选择一个功能:")
    for item in funcs:
        print(item)
    # 提示用户输入
    try:
        choice = int(input(f"请输入功能编号 (1-{len(funcs)}): "))
        if choice == 1:
            run_update_bugly()
        elif choice == 2:
            run_exc_lang_to_localizable_files()
        elif choice == 3:
            run_exc_org_match_rep()
        elif choice == 4:
            run_podfile_handle()
        elif choice == 5:
            run_download_medias()
        elif choice == 6:
            run_strings_replace()
        elif choice == 7:
            run_ffmpeg_make()
        elif choice == 8:
            # 重置后继续执行
            reset_cache()
            running()
        elif choice == 9:
            run_excel_match_to_replace()
        else:
            print(f"无效的选择，请输入 1 到 {len(funcs)} 之间的数字。")
    except ValueError:
            print("输入无效，请输入数字。")


if __name__ == "__main__":
    running()

