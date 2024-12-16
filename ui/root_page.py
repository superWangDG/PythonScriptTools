from kivy.graphics import Color, Rectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from localization.localization import get_localized_text
from utils.color_utils import ColorUtils


class RootPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 设置背景颜色
        with self.canvas.before:
            Color(*ColorUtils.hex_to_rgba("#F2C745"))  # 使用十六进制颜色
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        # 初始化布局
        self.setup_ui()

    def update_rect(self, instance, value):
        # 更新背景矩形大小
        self.rect.pos = self.pos
        self.rect.size = self.size

    def setup_ui(self):
        # 创建 RecycleView 组件
        table_view = RecycleView()
        table_view.viewclass = RootItemDivider
        table_view.layout = RecycleBoxLayout(orientation='vertical', default_size=(None, 50), size_hint_y=None)
        table_view.layout.bind(minimum_height=table_view.setter('height'))

        # 设置数据源（即每行需要的内容）
        func_list = [
            get_localized_text("bugly_dsym_upload"),
            get_localized_text("excel_generate_dev_file"),
            get_localized_text("excel_file_language_replace")
        ]

        # 设置表格项
        table_view.data = [{'item': item} for item in func_list]

        # 将 RecycleView 添加到页面
        self.add_widget(table_view)

    def on_button_click(self, instance, text):
        print(f"Button '{text}' clicked!")


class RootItemDivider(BoxLayout):
    def __init__(self, item, **kwargs):
        super().__init__(**kwargs)
        print("初始化了 Item")
        self.orientation = 'vertical'  # 垂直布局

        # 创建按钮
        button = Button(text=item, size_hint_y=None, height=50)
        # button.bind(on_press=lambda instance, text=item)
        self.add_widget(button)

        # 创建分割线
        divider = Widget(size_hint_y=None, height=2)
        with divider.canvas:
            Color(0, 0, 0, 1)  # 设置颜色为黑色
            Line(rectangle=(0, 0, divider.width, divider.height), width=2)  # 绘制分割线
        self.add_widget(divider)


    # def __init__(self, on_button_click, **kwargs):
    #     super().__init__(**kwargs)
    #     self.orientation = 'vertical'  # 垂直布局
    #
    #     # 功能列表
    #     func_list = [
    #         get_localized_text("bugly_dsym_upload"),
    #         get_localized_text("excel_generate_dev_file"),
    #         get_localized_text("excel_file_language_replace")
    #     ]
    #
    #     # 为每个功能创建按钮和分割线
    #     for item in func_list:
    #         button = Button(text=item, size_hint_y=None, height=50)
    #         button.bind(on_press=lambda instance, text=item: on_button_click(instance, text))
    #         self.add_widget(button)
    #
    #         # 添加分割线
    #         divider = Widget(size_hint_y=None, height=2)
    #         with divider.canvas:
    #             Color(0, 0, 0, 1)  # 设置颜色为黑色
    #             Line(rectangle=(0, 0, divider.width, divider.height), width=2)  # 绘制分割线
    #         self.add_widget(divider)
