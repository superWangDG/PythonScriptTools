# 读取文件夹内的 Excel 表格将内容匹配替换
import pandas as pd
import os
import subprocess
import platform


def open_folder(path):
    # 获取当前脚本所在的文件夹路径
    # 根据不同的操作系统选择适当的命令来打开文件夹
    if platform.system() == 'Windows':
        os.startfile(path)  # Windows
    elif platform.system() == 'Darwin':  # macOS
        subprocess.run(['open', path])
    else:  # Linux
        subprocess.run(['xdg-open', path])


def load_files(directory):
    # 构造文件路径
    source_file_path = os.path.join(directory, 'source.xlsx')
    replace_file_path = os.path.join(directory, 'replace.xlsx')

    if not os.path.exists(source_file_path):
        print(f"Source file {source_file_path} does not exist.")
        return None, None

    if not os.path.exists(replace_file_path):
        print(f"Replace file {replace_file_path} does not exist.")
        return None, None

    source_df = pd.read_excel(source_file_path)
    replace_df = pd.read_excel(replace_file_path)

    return source_df, replace_df


def find_key_row(source_df):
    """
    在 DataFrame 中查找包含 'Key' 的行。
    """
    for idx, row in source_df.iterrows():
        if "Key" in row.values:
            return idx  # 返回包含 'Key' 的行号
    return -1  # 如果没有找到，返回 -1


def replace_values(source_df, replace_df):
    """
      替换源文件中的指定内容，基于替换文件的内容。
      """
    # 创建一个新的 DataFrame 保存替换后的结果
    result_df = source_df.copy()

    # 查找替换文件中包含 "Key" 的行，作为列头
    key_row_index = replace_df[replace_df.iloc[:, 0] == "Key"].index[0]
    replace_keys = replace_df.iloc[key_row_index]  # 替换文件的列名行

    # 遍历源文件的每一行
    while True:
        print("请输入需要替换的类型(输入0或者直接回车的情况下替换所有类型):")
        def_list = list(replace_keys[1:])  # 可替换的类型列表

        for idx, language in enumerate(def_list, start=1):
            print(f"{idx}: {language}")

        # 获取用户输入
        type_input = input("请输入对应的数值: ").strip()
        try:
            # 将输入转换为整数并验证
            type_value = int(type_input) if type_input else 0

            choose_language = def_list[type_value - 1]
            break
        except (ValueError, IndexError):
            print(f"输入无效: {type_input}, 请重新输入!")

    key_col_index = source_df[source_df.iloc[:, 0] == "Key"].index[0]
    # 获取用户选择语言的列下标
    try:
        language_col_index = source_df.columns.get_loc(
            source_df.iloc[key_row_index, :][source_df.iloc[key_row_index, :] == choose_language].index[0]
        )
    except IndexError:
        print("选择全部语言")

    for idx, row in source_df.iterrows():
        if idx <= key_col_index + 1:
            continue
        # 确定开始替换的行
        replace_key = row.iloc[0]
        replace_value = row.iloc[key_col_index]
        vals = replace_df.iloc[key_col_index + 1:]
        for replace_index, replace_item in vals.iterrows():
            if replace_item.iloc[0] == replace_key:
                if type_value != 0:
                    # 单个语言替换
                    result_df.iat[idx, language_col_index] = replace_item.iloc[type_value]
                    print(f"输出单个替换: {replace_key}, oldValue: {replace_value}, newValue: {replace_item.iloc[type_value]}")
                else:
                    # 所有语言替换
                    print("替换所有暂不支持")
                break

    return result_df


def save_result(directory, result_df):
    # 构造输出文件路径
    output_file_path = os.path.join(directory, 'result.xlsx')
    result_df.to_excel(output_file_path, index=False)
    print(f"Result saved to {output_file_path}")


def main():
    # 输入目标目录
    # directory = input("Enter the target directory: ").strip()
    directory = "/Users/apple/Downloads/替换"
    # 载入文件
    source_df, replace_df = load_files(directory)

    if source_df is None or replace_df is None:
        return

    print("---------------准备开始替换文本----------------")
    # 替换内容
    result_df = replace_values(source_df, replace_df)
    # 保存结果
    save_result(directory, result_df)
    print("---------------替换文本结束----------------")
    # 打开文件夹
    open_folder(directory)


if __name__ == "__main__":
    main()
