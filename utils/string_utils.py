import re

# 帕斯卡命名
def to_pascal_case(text):
    words = re.split(r'[^a-zA-Z]', text)
    words = [word for word in words if word]
    return ''.join(word.capitalize() for word in words)

# 驼峰命名
def to_camel_case(text):
    # 使用正则表达式分割字符串，匹配所有非字母字符作为分隔符
    words = re.split(r'[^a-zA-Z]', text)
    # 过滤掉空字符串
    words = [word for word in words if word]
    if not words:
        return ""
    # 第一个单词小写，其余单词首字母大写
    camel_case = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    return camel_case
