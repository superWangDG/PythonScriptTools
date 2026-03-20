import os
import re

from utils.cache_utils import get_list_use_folder_cache, load_from_cache
from utils.file_utils import open_folder


# ─── 扫描 NSLocalizedString ──────────────────────────────────────────────────

NSLOC_PATTERN = re.compile(
    r'NSLocalizedString\s*\(\s*'
    r'(?:'
    r'"((?:[^"\\]|\\.)*)"'           # group(1): 字符串字面量 key
    r'|'
    r'([A-Za-z_]\w*(?:\.\w+)*)'      # group(2): 属性/变量引用
    r')',
    re.MULTILINE
)

# Swift/ObjC 关键字，动态引用时过滤
_SKIP_KEYWORDS = {"nil", "true", "false", "self", "super"}


def _build_line_starts(content: str) -> list[int]:
    starts = [0]
    for i, c in enumerate(content):
        if c == '\n':
            starts.append(i + 1)
    return starts


def _offset_to_lineno(line_starts: list[int], offset: int) -> int:
    lo, hi = 0, len(line_starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if line_starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


def scan_source_files(root_folder: str):
    """
    递归扫描 .swift / .m / .h，找出所有 NSLocalizedString 调用。

    返回：
      literal_keys : { key: [(rel_path, lineno), ...] }   字面量 key（严格原文）
      dynamic_refs : { ref: [(rel_path, lineno), ...] }   属性/变量引用
    """
    literal_keys: dict[str, list[tuple[str, int]]] = {}
    dynamic_refs: dict[str, list[tuple[str, int]]] = {}

    for dirpath, _, files in os.walk(root_folder):
        if any(part.endswith(".lproj") for part in dirpath.split(os.sep)):
            continue

        for filename in sorted(files):
            if not filename.endswith((".swift", ".m", ".h")):
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_folder)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, OSError):
                print(f"  ⚠️  无法读取：{rel_path}")
                continue

            line_starts = _build_line_starts(content)

            for m in NSLOC_PATTERN.finditer(content):
                lineno = _offset_to_lineno(line_starts, m.start())
                literal = m.group(1)
                dynamic = m.group(2)

                if literal is not None:
                    key = literal.replace('\\"', '"')
                    entry = (rel_path, lineno)
                    literal_keys.setdefault(key, [])
                    if entry not in literal_keys[key]:
                        literal_keys[key].append(entry)

                elif dynamic is not None:
                    if dynamic not in _SKIP_KEYWORDS:
                        entry = (rel_path, lineno)
                        dynamic_refs.setdefault(dynamic, [])
                        if entry not in dynamic_refs[dynamic]:
                            dynamic_refs[dynamic].append(entry)

    return literal_keys, dynamic_refs


# ─── 解析 .strings ────────────────────────────────────────────────────────────

def _strip_comments(content: str) -> str:
    result = []
    i = 0
    n = len(content)
    in_string = False
    while i < n:
        c = content[i]
        if in_string:
            if c == '\\' and i + 1 < n:
                result.append(c); result.append(content[i + 1]); i += 2
            elif c == '"':
                result.append(c); in_string = False; i += 1
            else:
                result.append(c); i += 1
        else:
            if c == '"':
                in_string = True; result.append(c); i += 1
            elif c == '/' and i + 1 < n and content[i + 1] == '*':
                i += 2
                while i < n - 1:
                    if content[i] == '*' and content[i + 1] == '/': i += 2; break
                    i += 1
                result.append(' ')
            elif c == '/' and i + 1 < n and content[i + 1] == '/':
                while i < n and content[i] != '\n': i += 1
            else:
                result.append(c); i += 1
    return ''.join(result)


def parse_strings_keys(filepath: str) -> set[str]:
    """解析单个 .strings 文件，返回已声明的 key 集合（保留原始大小写）。"""
    keys = set()
    for enc in ("utf-8-sig", "utf-8", "utf-16"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        return keys

    content = _strip_comments(content)
    pattern = re.compile(r'"((?:[^"\\]|\\.)*?)"\s*=\s*"', re.DOTALL)
    for m in pattern.finditer(content):
        key = m.group(1).replace('\\"', '"')
        keys.add(key)
    return keys


def collect_strings_keys(root_folder: str) -> set[str]:
    """
    扫描所有 .lproj 内的 .strings，返回全局已声明 key 集合（所有语言合并）。
    """
    all_keys: set[str] = set()
    for dirpath, dirnames, _ in os.walk(root_folder):
        for d in dirnames:
            if not d.endswith(".lproj"):
                continue
            lproj_path = os.path.join(dirpath, d)
            for f in os.listdir(lproj_path):
                if f.endswith(".strings"):
                    all_keys |= parse_strings_keys(os.path.join(lproj_path, f))
    return all_keys


# ─── 分类：完全匹配 / 大小写不一致 / 完全缺失 ────────────────────────────────

def classify_keys(
    literal_keys: dict[str, list[tuple[str, int]]],
    declared_keys: set[str],
):
    """
    将源码字面量 key 分为三类：

    exact_match    : key 在 .strings 中完全一致（正常，不输出）
    case_mismatch  : { source_key: (strings_key, [(rel_path, lineno)]) }
                     源码 key 与 .strings key 仅大小写不同
    missing        : { key: [(rel_path, lineno)] }
                     在所有 .strings 中完全找不到
    """
    # 构建小写 → 原始 key 的映射（用于大小写对比）
    lower_to_declared: dict[str, str] = {}
    for k in declared_keys:
        lower_to_declared[k.lower()] = k

    case_mismatch: dict[str, tuple[str, list[tuple[str, int]]]] = {}
    missing: dict[str, list[tuple[str, int]]] = {}

    for key, locations in literal_keys.items():
        if key in declared_keys:
            # 完全匹配，跳过
            continue
        lower_key = key.lower()
        if lower_key in lower_to_declared:
            # 大小写不一致
            strings_key = lower_to_declared[lower_key]
            case_mismatch[key] = (strings_key, locations)
        else:
            # 完全缺失
            missing[key] = locations

    return case_mismatch, missing


# ─── 输出文件 ─────────────────────────────────────────────────────────────────

def _write_file(path: str, lines: list[str]):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  → {path}")


def write_outputs(
    literal_keys: dict[str, list[tuple[str, int]]],
    dynamic_refs: dict[str, list[tuple[str, int]]],
    case_mismatch: dict[str, tuple[str, list[tuple[str, int]]]],
    missing: dict[str, list[tuple[str, int]]],
    output_dir: str,
    folder_name: str,
):
    # ── 文件一：所有字面量 key + 文件地址:行号 ───────────────────────────────
    lines = [f"# 字面量 key（共 {len(literal_keys)} 个）", ""]
    for key, locations in literal_keys.items():
        lines.append(key)
        for rel_path, lineno in locations:
            lines.append(f"    {rel_path}:{lineno}")
        lines.append("")
    _write_file(os.path.join(output_dir, f"{folder_name}_1_all_keys.txt"), lines)

    # ── 文件二：动态引用变量 + 文件地址:行号 ─────────────────────────────────
    lines = [f"# 动态引用（属性/变量，共 {len(dynamic_refs)} 个）— 需人工确认", ""]
    if dynamic_refs:
        for ref, locations in dynamic_refs.items():
            lines.append(ref)
            for rel_path, lineno in locations:
                lines.append(f"    {rel_path}:{lineno}")
            lines.append("")
    else:
        lines.append("（无动态引用）")
    _write_file(os.path.join(output_dir, f"{folder_name}_2_dynamic_refs.txt"), lines)

    # ── 文件三：大小写不一致 key ──────────────────────────────────────────────
    lines = [f"# 大小写不一致（共 {len(case_mismatch)} 个）— 源码与 .strings 大小写不同", ""]
    if case_mismatch:
        for src_key, (str_key, locations) in case_mismatch.items():
            lines.append(f"源码  : {src_key}")
            lines.append(f"strings: {str_key}")
            for rel_path, lineno in locations:
                lines.append(f"    {rel_path}:{lineno}")
            lines.append("")
    else:
        lines.append("（无大小写不一致）")
    _write_file(os.path.join(output_dir, f"{folder_name}_3_case_mismatch.txt"), lines)

    # ── 文件四：完全缺失的 key ────────────────────────────────────────────────
    lines = [f"# 未在任何 .strings 中声明的 key（共 {len(missing)} 个）", ""]
    if missing:
        for key, locations in missing.items():
            lines.append(key)
            for rel_path, lineno in locations:
                lines.append(f"    {rel_path}:{lineno}")
            lines.append("")
    else:
        lines.append("✅ 全部 key 均已声明，无遗漏。")
    _write_file(os.path.join(output_dir, f"{folder_name}_4_missing_keys.txt"), lines)


# ─── 入口 ─────────────────────────────────────────────────────────────────────

def run_scan_localized_strings():
    print("=== NSLocalizedString 扫描工具 ===\n")

    cache_json = load_from_cache() or {}
    root_folder = get_list_use_folder_cache(cache_json, "ScanLocalizedString")
    if not root_folder:
        print("❌ 未选择文件夹，已取消。")
        return

    print(f"\n📂 目标文件夹：{root_folder}")

    # 1. 扫描源码
    print("🔍 正在扫描源码中的 NSLocalizedString...")
    literal_keys, dynamic_refs = scan_source_files(root_folder)
    print(f"   字面量 key：{len(literal_keys)} 个")
    print(f"   动态引用：  {len(dynamic_refs)} 个")

    # 2. 扫描 .strings
    print("🔍 正在扫描 .lproj 中的 .strings 文件...")
    declared_keys = collect_strings_keys(root_folder)
    print(f"   已声明 key：{len(declared_keys)} 个")

    # 3. 分类
    case_mismatch, missing = classify_keys(literal_keys, declared_keys)
    print(f"   大小写不一致：{len(case_mismatch)} 个")
    print(f"   完全缺失：    {len(missing)} 个")

    # 4. 输出四个文件
    output_dir = os.path.join(root_folder, "output")
    os.makedirs(output_dir, exist_ok=True)
    folder_name = os.path.basename(root_folder.rstrip("/\\"))

    print("\n📝 正在生成报告文件...")
    write_outputs(literal_keys, dynamic_refs, case_mismatch, missing, output_dir, folder_name)

    print("\n✅ 完成")
    open_folder(output_dir)


if __name__ == "__main__":
    run_scan_localized_strings()