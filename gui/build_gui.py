"""Build the GUI app with PyInstaller."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
GUI_ENTRY = ROOT_DIR / "gui" / "app.py"
OUTPUT_DIR = ROOT_DIR / "gui" / "output"
BUILD_DIR = ROOT_DIR / "gui" / "build"
SPEC_DIR = ROOT_DIR / "gui" / "spec"
APP_NAME = "CloudHearingToolsGUI"


def ensure_pyinstaller() -> None:
    if shutil.which("pyinstaller"):
        return

    print("未检测到 pyinstaller，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def ensure_tkinter() -> None:
    try:
        import tkinter  # noqa: F401
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "当前 Python 环境缺少 tkinter/_tkinter，无法运行或打包 GUI。\n"
            "macOS 建议安装带 Tcl/Tk 的 Python，例如 python.org 官方安装包，"
            "或使用支持 tkinter 的解释器重新执行 gui/build_gui.py。"
        ) from exc


def build() -> None:
    ensure_tkinter()
    ensure_pyinstaller()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)

    data_separator = ";" if os.name == "nt" else ":"
    add_data = f"{ROOT_DIR / 'localization' / 'localization.json'}{data_separator}localization"

    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "--distpath",
        str(OUTPUT_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(SPEC_DIR),
        "--add-data",
        add_data,
        "--paths",
        str(ROOT_DIR),
        str(GUI_ENTRY),
    ]

    print("开始打包 GUI...")
    subprocess.check_call(command, cwd=str(ROOT_DIR))
    print(f"打包完成：{OUTPUT_DIR}")


if __name__ == "__main__":
    build()
