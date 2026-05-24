"""Tkinter GUI wrapper for the existing automation scripts."""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

try:
    from gui.tasks import TASKS
except ModuleNotFoundError:
    from tasks import TASKS


ROOT_DIR = Path(__file__).resolve().parents[1]
IS_FROZEN = getattr(sys, "frozen", False)
WORK_DIR = Path(sys.executable).resolve().parent if IS_FROZEN else ROOT_DIR


def run_task_cli(task_id: int) -> None:
    from scene.auto_download_holiday import run_recursive_download
    from scene.excel_language_generate_key import run_excel_language_generate_key
    from scene.excel_match_replace import run_excel_match_to_replace
    from scene.excel_orgifile_match_replace import run_exc_org_match_rep
    from scene.ffmpeg_donwload_files import run_download_medias
    from scene.ffmpeg_source_code_to_lib import run_ffmpeg_make
    from scene.ios_podfile_handle import run_podfile_handle
    from scene.ios_strings_out_excel import run_lproj_to_excel
    from scene.language_to_localizable import run_exc_lang_to_localizable_files
    from scene.merge_strings import merge_strings_files
    from scene.reset_cache import reset_cache
    from scene.run_scan_localized import run_scan_localized_strings
    from scene.strings_replace import run_strings_replace
    from scene.upload_bugly import run_update_bugly

    task_map = {
        1: run_update_bugly,
        2: run_exc_lang_to_localizable_files,
        3: run_exc_org_match_rep,
        4: run_podfile_handle,
        5: run_download_medias,
        6: run_strings_replace,
        7: run_ffmpeg_make,
        8: reset_cache,
        9: run_excel_match_to_replace,
        10: lambda: merge_strings_files(
            "/Users/wangdegui/Documents/Test/Orgi_Localizable.strings",
            "/Users/wangdegui/Documents/Test/New_Localizable.strings",
            "/Users/wangdegui/Documents/Test/Localizable_merge.strings",
        ),
        11: run_excel_language_generate_key,
        12: run_recursive_download,
        13: run_lproj_to_excel,
        14: run_scan_localized_strings,
    }

    task = task_map.get(task_id)
    if not task:
        raise ValueError(f"未知功能编号：{task_id}")
    task()


if len(sys.argv) == 3 and sys.argv[1] == "--run-task":
    run_task_cli(int(sys.argv[2]))
    sys.exit(0)


import tkinter as tk
from tkinter import messagebox, ttk


class AutomationGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CloudHearing Python 自动化工具")
        self.geometry("1080x720")
        self.minsize(920, 620)

        self.process: subprocess.Popen[str] | None = None
        self.output_queue: queue.Queue[str] = queue.Queue()
        self.selected_task_id = tk.IntVar(value=TASKS[0]["id"])

        self._build_style()
        self._build_layout()
        self._poll_output()

    def _build_style(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        bg = "#f5f7fb"
        panel = "#ffffff"
        accent = "#2563eb"
        text = "#111827"

        self.configure(bg=bg)
        style.configure(".", font=("Arial", 13), background=bg, foreground=text)
        style.configure("TFrame", background=bg)
        style.configure("Panel.TFrame", background=panel)
        style.configure("Title.TLabel", font=("Arial", 20, "bold"), background=bg, foreground=text)
        style.configure("Muted.TLabel", font=("Arial", 12), background=bg, foreground="#6b7280")
        style.configure("Task.TRadiobutton", font=("Arial", 13), background=panel, foreground=text, padding=8)
        style.configure("Primary.TButton", font=("Arial", 13, "bold"), padding=(14, 9))
        style.map("Primary.TButton", foreground=[("active", "#ffffff")], background=[("active", accent)])

    def _build_layout(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", padx=22, pady=(18, 10))

        ttk.Label(header, text="CloudHearing Python 自动化工具", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="选择功能后点击运行；脚本执行时如出现命令行提示，可在底部输入框继续输入。",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(5, 0))

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        body.columnconfigure(0, minsize=330, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        task_panel = ttk.Frame(body, style="Panel.TFrame")
        task_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        ttk.Label(task_panel, text="功能列表", font=("Arial", 15, "bold"), background="#ffffff").pack(
            anchor="w", padx=16, pady=(16, 8)
        )

        task_canvas = tk.Canvas(task_panel, bg="#ffffff", highlightthickness=0)
        task_scroll = ttk.Scrollbar(task_panel, orient="vertical", command=task_canvas.yview)
        task_list = ttk.Frame(task_canvas, style="Panel.TFrame")
        task_list.bind("<Configure>", lambda event: task_canvas.configure(scrollregion=task_canvas.bbox("all")))
        task_canvas.create_window((0, 0), window=task_list, anchor="nw")
        task_canvas.configure(yscrollcommand=task_scroll.set)
        task_canvas.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 14))
        task_scroll.pack(side="right", fill="y", pady=(0, 14))

        for task in TASKS:
            text = f'{task["id"]}. {task["title"]}\n{task["description"]}'
            ttk.Radiobutton(
                task_list,
                text=text,
                value=task["id"],
                variable=self.selected_task_id,
                style="Task.TRadiobutton",
            ).pack(fill="x", padx=8, pady=2)

        work_panel = ttk.Frame(body)
        work_panel.grid(row=0, column=1, sticky="nsew")
        work_panel.rowconfigure(1, weight=1)
        work_panel.columnconfigure(0, weight=1)

        toolbar = ttk.Frame(work_panel)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.run_button = ttk.Button(toolbar, text="运行选中功能", style="Primary.TButton", command=self.run_task)
        self.run_button.pack(side="left")

        self.stop_button = ttk.Button(toolbar, text="停止", command=self.stop_task, state="disabled")
        self.stop_button.pack(side="left", padx=(10, 0))

        ttk.Button(toolbar, text="清空日志", command=self.clear_log).pack(side="left", padx=(10, 0))
        ttk.Button(toolbar, text="打开项目目录", command=self.open_project_folder).pack(side="right")

        console_frame = ttk.Frame(work_panel, style="Panel.TFrame")
        console_frame.grid(row=1, column=0, sticky="nsew")
        console_frame.rowconfigure(0, weight=1)
        console_frame.columnconfigure(0, weight=1)

        self.console = tk.Text(
            console_frame,
            bg="#0f172a",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            relief="flat",
            wrap="word",
            font=("Menlo", 12),
            padx=14,
            pady=14,
        )
        console_scroll = ttk.Scrollbar(console_frame, orient="vertical", command=self.console.yview)
        self.console.configure(yscrollcommand=console_scroll.set)
        self.console.grid(row=0, column=0, sticky="nsew")
        console_scroll.grid(row=0, column=1, sticky="ns")

        input_bar = ttk.Frame(work_panel)
        input_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        input_bar.columnconfigure(0, weight=1)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_bar, textvariable=self.input_var, font=("Arial", 13))
        self.input_entry.grid(row=0, column=0, sticky="ew")
        self.input_entry.bind("<Return>", self.send_input)

        ttk.Button(input_bar, text="发送输入", command=self.send_input).grid(row=0, column=1, padx=(10, 0))

        self._append_log("GUI 已就绪。请选择左侧功能后运行。\n")

    def run_task(self) -> None:
        if self.process and self.process.poll() is None:
            messagebox.showinfo("正在运行", "已有任务正在执行，请先停止或等待完成。")
            return

        task_id = self.selected_task_id.get()
        task = next(item for item in TASKS if item["id"] == task_id)
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        self._append_log(f"\n=== 开始执行：{task_id}. {task['title']} ===\n")
        command = [sys.executable, "--run-task", str(task_id)] if IS_FROZEN else [
            sys.executable,
            "-u",
            str(Path(__file__).resolve()),
            "--run-task",
            str(task_id),
        ]

        self.process = subprocess.Popen(
            command,
            cwd=str(WORK_DIR),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )

        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        threading.Thread(target=self._read_process_output, daemon=True).start()

    def _read_process_output(self) -> None:
        if not self.process or not self.process.stdout:
            return

        for line in self.process.stdout:
            self.output_queue.put(line)

        return_code = self.process.wait()
        self.output_queue.put(f"\n=== 任务结束，返回码：{return_code} ===\n")
        self.output_queue.put("__PROCESS_DONE__")

    def _poll_output(self) -> None:
        try:
            while True:
                item = self.output_queue.get_nowait()
                if item == "__PROCESS_DONE__":
                    self.run_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self.process = None
                else:
                    self._append_log(item)
        except queue.Empty:
            pass

        self.after(100, self._poll_output)

    def send_input(self, event: tk.Event | None = None) -> None:
        value = self.input_var.get()
        if not value:
            return

        if not self.process or self.process.poll() is not None or not self.process.stdin:
            messagebox.showinfo("没有运行中的任务", "请先运行一个功能。")
            return

        self._append_log(f"> {value}\n")
        self.process.stdin.write(value + "\n")
        self.process.stdin.flush()
        self.input_var.set("")

    def stop_task(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self._append_log("\n已请求停止当前任务。\n")

    def clear_log(self) -> None:
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="normal")

    def open_project_folder(self) -> None:
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(WORK_DIR)])
        elif os.name == "nt":
            os.startfile(WORK_DIR)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(WORK_DIR)])

    def _append_log(self, text: str) -> None:
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.configure(state="normal")


def main() -> None:
    app = AutomationGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
