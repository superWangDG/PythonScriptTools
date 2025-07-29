import re

def parse_strings_file(path):
    entries = {}
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                match = re.match(r'^\s*"([^"]+)"\s*=\s*"([^"]*)";', line)
                if match:
                    key, value = match.groups()
                    entries[key] = value
    except Exception as e:
        print(f"❌ 解析文件失败: {path}\n错误信息: {e}")
        raise
    return entries

def merge_strings_files(root_path, old_path, output_path):
    print("进入处理")
    root_entries = parse_strings_file(root_path)
    old_entries = parse_strings_file(old_path)

    # 替换 old_entries 中匹配 key 的 value
    merged_entries = {}
    for key in old_entries:
        if key in root_entries:
            merged_entries[key] = root_entries[key]  # 用 root 的值替换
        else:
            merged_entries[key] = old_entries[key]   # 保留原值

    # 写入 output_path 文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for key in sorted(merged_entries.keys()):
                value = merged_entries[key]
                f.write(f'"{key}" = "{value}";\n')
        print(f"✅ 合并完成，写入: {output_path}")
    except Exception as e:
        print(f"❌ 写入文件失败: {output_path}\n错误信息: {e}")
        raise


    # print("进入处理222")
    # # 添加旧文件中独有的 key
    # for key, value in old_entries.items():
    #     if key not in root_entries:
    #         root_entries[key] = value
    #
    # # 按 key 排序后写入输出文件
    # with open(output_path, 'w', encoding='utf-8') as f:
    #     for key in sorted(root_entries.keys()):
    #         f.write(f'"{key}" = "{root_entries[key]}";\n')
    #
    # print(f"✅ 合并完成！输出文件：{output_path}")

