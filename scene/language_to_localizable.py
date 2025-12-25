# 使用表格中的多语言文件生成对应系统的应用文件

import pandas as pd
import os
import shutil
import re

from utils.cache_utils import load_from_cache, save_to_cache, get_list_use_folder_cache
from utils.file_utils import open_folder, select_source, find_exc_file
from localization.localization import get_localized_text


# 开始处理 excel 转为 本地化的语言
def create_files_from_excel(file_path, output_dir):
    # 读取 Excel 文件 keep_default_na 不处理表格中的 nan 值原数据返回
    df = pd.read_excel(file_path, keep_default_na=False)
    # 找到 Key 行及之后的内容
    key_row_index = df[df.iloc[:, 0] == "Key"].index[0]
    data_start = key_row_index + 1
    # 得到创建文件的声明
    dir_dict_data = get_dir_data_dict(df.iloc[0:data_start - 1])
    content_df = df.iloc[data_start:].reset_index(drop=True)

    for key, value in dir_dict_data.items():
        # 判断对应平台是否同时存在 file | folder
        if "file" in value and "folder" in value:
            # 创建文件夹以及得到语言写入的地址
            dir_dict_data[key]["writes"] = create_localizable_dir(key, value, output_dir)

    print(f"output df content length: {len(content_df)}")

    # 开始遍历表格内容的数据并且生成指定的本地化语言文件
    for idx, row in content_df.iterrows():
        column_key = row.values[0]
        # 🚫 key 为 NaN / 空字符串 / 纯空格 → 跳过
        if not isinstance(column_key, str) or not column_key.strip():
            continue
        # 检查并处理 column_key
        if pd.isna(column_key):  # 判断是否是 NaN
            column_key = "None"  # 将 NaN 转为空字符串
        elif column_key == "None":  # 字符串 'None' 保留
            column_key = "None"
        # 测试特殊打印
        # if idx == 264:
        # print(f"输出当前的 索引为None: {idx}, item列表: {row}\n {type(column_key)}，key: {column_key} ")
        values = row.iloc[1:]
        for r_idx, r_column in enumerate(values):
            # 如果 r_column 为空字符串，则查找 values 中下一个非空字符串
            if not isinstance(r_column, str) or not r_column.strip():
                r_column = get_valid_value(values, 0)
            for key, value in dir_dict_data.items():
                print("DEBUG value =", value)
                print("AVAILABLE KEYS =", value.keys())
                file_path = value["writes"][r_idx]
                writer_data(file_path, column_key, values, r_idx, r_column, key, idx, len(content_df))


def get_valid_value(values, start_idx):
    """
    获取 `values` 列表中从 `start_idx` 开始的第一个非空字符串值
    如果全部为空，则返回空字符串 `""`
    """
    for i in range(start_idx, len(values)):  # 从当前索引开始遍历
        val = values.iloc[i]  # 确保使用 `.iloc` 访问按位置取值
        if isinstance(val, str) and val.strip():  # 确保是非空字符串
            return val
    return ""  # 如果全部为空，则返回空字符串


def writer_data(file_path, column_key, columns, col_idx, col_val, target_platform, row_idx, max_row_len):
    # flutter 需要单独处理创建一个strings的文件
    if target_platform == "Flutter" and col_idx == 0:
        strings_path = os.path.join(os.path.dirname(os.path.dirname(file_path)), "strings.dart")
        with open(strings_path, "a", encoding="utf-8") as f:
            if row_idx == 0:
                f.write("class StrRes {\n")
            key = 'continueStr' if column_key == 'continue' else column_key
            f.write(f"\tstatic get {key} => '{column_key}'.tr;\n")
            if row_idx + 1 == max_row_len:
                f.write("}")

    with open(file_path, "a", encoding="utf-8") as f:
        if pd.isna(col_val) and col_idx == 0:  # 判断是否是 NaN
            col_val = "None"
        elif pd.isna(col_val) and col_idx != 0:
            # col_val = columns.iloc[0]  # 使用 values 的第一个数据赋值
            # 找到第一个非空的值
            col_val = next((val for val in columns if isinstance(val, str) and val.strip()), "None")

        # 替换表格中的原本换行操作
        col_val = escape_excel_newline(col_val)
        # 判断 值内的内容是否存在" 并且没有添加转义符号
        col_val = escape_unescaped_quotes(col_val)
        # 处理非法的转义符号
        col_val = sanitize_backslash(col_val)

        if target_platform == "iOS":
            # iOS 的存储
            col_val = escape_android_unit_to_ios(col_val)
            # 开始写入数据
            f.write(f"\"{column_key}\" = \"{col_val}\";\n")
        elif target_platform == "Android":
            # 文件的开头
            if row_idx == 0:
                f.write(f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<resources>\n")
            # 写入实际的数据
            col_val = escape_ios_unit_to_android(col_val)
            f.write(f"\t<string name=\"{column_key}\">{col_val}</string>\n")
            # 文件的结尾
            if row_idx + 1 == max_row_len:
                f.write(f"</resources>")
        elif target_platform == "Flutter":
            if row_idx == 0:
                filename = os.path.basename(file_path).split(".")[0]
                last = "{"
                f.write(f"const Map<String, String> {filename} = {last}\n")
            f.write(f"\t\"{column_key}\": \"{col_val}\",\n")
            if row_idx + 1 == max_row_len:
                f.write("};")
            """
            增加 arb 的生成
            """
            intl_arb_path = get_flutter_intl_arb_path(file_path)

            with open(intl_arb_path, "a", encoding="utf-8") as arb_f:
                if row_idx == 0:
                    arb_f.write("{\n")
                    arb_f.write(f'\t"@@locale": "{filename}",\n')

                is_last = (row_idx + 1 == max_row_len)

                if is_last:
                    arb_f.write(f'\t"{column_key}": "{col_val}"\n')
                    arb_f.write("}")
                else:
                    arb_f.write(f'\t"{column_key}": "{col_val}",\n')



def get_flutter_intl_arb_path(file_path: str) -> str:
    """
    langs/en.dart -> langs/intl_en.arb
    """
    dirname = os.path.dirname(file_path)
    filename = os.path.basename(file_path).split(".")[0]  # en
    return os.path.join(dirname, f"intl_{filename}.arb")


# 使用正则表达式查找并转义未转义的双引号
def escape_unescaped_quotes(text):
    if isinstance(text, str):
        return re.sub(r'(?<!\\)"', r'\\"', text)
    else:
        # 如果不是字符串，返回原始值或其他默认值
        return text


def sanitize_backslash(text):
    """
    防止错误的反斜杠：
    - 如果字符串是单个 \ 或 \ 后没有跟字符 → 返回空字符串
    - 合法转义保留，如 \\ \n \t
    """
    if not isinstance(text, str):
        return text

    # 全部 \ 替换为 placeholder
    placeholder = "__BACKSLASH__"
    text = text.replace("\\\\", placeholder)  # 先保护合法的 \\

    # 处理单独的 \ 或 \ 后没有字符
    # 正则：\ 结尾 或者 单独 \ （除了合法的 placeholder）
    if re.fullmatch(r"\\+", text):
        return ""
    # 如果 \ 在末尾，且不是合法 \\ → 去掉
    text = re.sub(r"\\$", "", text)

    # 恢复合法的 \\
    return text.replace(placeholder, "\\")


def escape_excel_newline(text):
    """
    只将 Excel 中的真实换行符转换为字符串 \\n
    不影响用户原本输入的 \\n
    """
    if not isinstance(text, str):
        return text

    # 先临时保护已经存在的 \n
    placeholder = "__EXISTING_NEWLINE__"
    text = text.replace("\\n", placeholder)

    # 将真实换行（Alt + Enter）转成 \n
    text = text.replace("\r\n", "\\n").replace("\n", "\\n")

    # 恢复原本的 \n
    return text.replace(placeholder, "\\n")

# 将Android 中的通用符号转为iOS中使用的符号
def escape_android_unit_to_ios(text):
    if isinstance(text, str):
        # 替换 %(数字)$s 为 %@
        text = re.sub(r'%\d+\$s', '%@', text)
        # 替换 %(数字)$d 为 %d
        text = re.sub(r'%\d+\$d', '%d', text)
        return text.replace("%s", "%@")
    else:
        # 如果不是字符串，返回原始值或其他默认值
        return text


# 将iOS 的通用符号转为Android使用的符号
def escape_ios_unit_to_android(text):
    if isinstance(text, str):
        # 替换 %(数字)$s 为 %@
        return text.replace("%@", "%s")
    else:
        # 如果不是字符串，返回原始值或其他默认值
        return text


# 获取文件夹以及文件的数据
def get_dir_data_dict(file_df):
    datalist = {}
    # 创建文件同时创建文件夹
    for idx, row in file_df.iterrows():
        # 增加第一行的信息
        columns = file_df.columns.tolist()
        columns_key = columns[0].split()[0]
        columns_value = columns[0].replace(columns_key, "").strip()
        if "Folder Name" in columns_value:
            # 文件夹的信息
            datalist.setdefault(columns_key, {})["folder"] = columns[1:]
        elif "File Name" in columns_value:
            datalist.setdefault(columns_key, {})["file"] = columns[1:]
        # 增加遍历的信息
        row_key = row.values[0].split()[0]
        row_value = row.values[0].replace(columns_key, "").strip()
        if "Folder Name" in row_value:
            # 文件夹的信息
            datalist.setdefault(row_key, {})["folder"] = row.values[1:]
        elif "File Name" in row_value:
            datalist.setdefault(row_key, {})["file"] = row.values[1:]
    return datalist


# 创建本地化的文件夹, 并返回目标文件的地址
def create_localizable_dir(target_platform, target_dict, root_path):
    file_path_list = []

    platform_root = os.path.join(root_path, target_platform)
    os.makedirs(platform_root, exist_ok=True)

    # ⭐ 关键：归一后的 folder 名 → 实际路径
    folder_map = {}

    folders = target_dict.get("folder", [])
    files = target_dict.get("file", [])

    for idx, raw_folder_name in enumerate(folders):
        normalized_folder = normalize_folder_name(raw_folder_name)

        # 同一个目录只创建一次
        if normalized_folder not in folder_map:
            folder_path = os.path.join(platform_root, normalized_folder)
            os.makedirs(folder_path, exist_ok=True)
            folder_map[normalized_folder] = folder_path

        # 文件写入归一后的目录
        if idx < len(files):
            file_path_list.append(
                os.path.join(folder_map[normalized_folder], files[idx])
            )

    return file_path_list


def normalize_folder_name(name: str) -> str:
    """
    仅当目录名以 .数字 结尾时，才认为是 pandas 的重复列后缀
    """
    if not isinstance(name, str):
        return name

    # 只处理 pandas 自动生成的后缀：.1 .2 .3 ...
    if re.search(r'\.\d+$', name):
        return re.sub(r'\.\d+$', '', name)

    return name


# 使用示例
def run_exc_lang_to_localizable_files():
    # 加载缓存
    result = get_list_use_folder_cache(load_from_cache(), "LanguageToLocalizable")
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
    create_files_from_excel(exc_path, output_directory)
    print(get_localized_text("complete_processing"))
    # 打开执行后的文件夹
    open_folder(output_directory)