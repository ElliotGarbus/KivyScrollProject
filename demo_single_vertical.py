from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.metrics import dp

from scrollview import ScrollView


class VerticalDemo(App):
    def build(self):
        root = ScrollView(do_scroll_x=False, do_scroll_y=True, scroll_type=['bars', 'content'], bar_width=dp(8), bar_color=[0.3, 0.6, 1.0, 0.8])
        content = GridLayout(cols=1, size_hint=(1, None))
        content.bind(minimum_height=content.setter('height'))
        for i in range(50):
            content.add_widget(Button(text=f"Item {i}", size_hint=(1, None), height=dp(60)))
        root.add_widget(content)

        # Simple debug prints
        return root


if __name__ == '__main__':
    VerticalDemo().run()


