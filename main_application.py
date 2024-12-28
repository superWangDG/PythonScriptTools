from scene.ios_podfile_handle import run_podfile_handle
from scene.upload_bugly import run_update_bugly
from scene.language_to_localizable import run_exc_lang_to_localizable_files
from scene.excel_orgifile_match_replace import run_exc_org_match_rep

if __name__ == "__main__":
    # 执行功能分选
    funcs = [
        "1.Bugly 符号表上传",
        "2.excel 文件开发多语言生成",
        "3.excel 指定的语言文本匹配替换",
        "4.执行iOS项目Cocoapods 的管理操作"
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
        else:
            print(f"无效的选择，请输入 1 到 {len(funcs)} 之间的数字。")
    except ValueError:
            print("输入无效，请输入数字。")

