

from scene.upload_bugly import run_update_bugly

if __name__ == "__main__":
    # 执行功能分选
    funcs = [
        "1.Bugly 符号表上传",
        "2.excel 文件开发多语言生成",
        "3.excel 指定的语言文本匹配替换"
    ]
    for item in funcs:

        # 打印功能选项
        print("请选择一个功能:")
        for item in funcs:
            print(item)

        # 提示用户输入
        try:
            choice = int(input("请输入功能编号 (1-3): "))
            if choice == 1:
                run_update_bugly()
            elif choice == 2:
                generate_multilanguage()
            elif choice == 3:
                replace_language_text()
            else:
                print("无效的选择，请输入 1 到 3 之间的数字。")
        except ValueError:
            print("输入无效，请输入数字。")
