# CloudHearing Python 自动化工具 GUI

这是现有终端脚本的 GUI 包装版本，业务逻辑仍然复用 `main_application.py` 和 `scene/` 目录中的脚本。

## 运行 GUI

```bash
python gui/app.py
```

选择左侧功能后点击「运行选中功能」。如果原脚本继续要求输入编号、路径或版本号，可以在底部输入框填写后发送。

## 打包 GUI

```bash
python gui/build_gui.py
```

打包产物会输出到：

```text
gui/output/CloudHearingToolsGUI
```

如果本机没有安装 `pyinstaller`，打包脚本会自动使用当前 Python 环境安装。

