from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.metrics import dp

from scrollview import ScrollView


class XYDemo(App):
    def build(self):
        root = ScrollView(do_scroll_x=True, do_scroll_y=True, scroll_type=['bars', 'content'], bar_width=dp(8), bar_color=[0.3, 0.6, 1.0, 0.8])
        grid = GridLayout(cols=20, spacing=dp(8), padding=dp(8), size_hint=(None, None))
        grid.bind(minimum_width=grid.setter('width'), minimum_height=grid.setter('height'))
        for i in range(400):
            grid.add_widget(Button(text=f"{i}", size_hint=(None, None), size=(dp(120), dp(80))))
        root.add_widget(grid)

        root.bind(on_scroll_start=lambda *_: print('[xy] start'),
                  on_scroll_move=lambda *_: print('[xy] move'),
                  on_scroll_stop=lambda *_: print('[xy] stop'))
        return root


if __name__ == '__main__':
    XYDemo().run()


