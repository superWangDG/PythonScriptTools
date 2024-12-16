# 图形化的App 启动页面
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from ui.root_page import RootPage


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(RootPage())
        return sm


if __name__ == "__main__":
    MyApp().run()
