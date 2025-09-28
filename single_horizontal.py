from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.metrics import dp

from updated_sv import ScrollView


class HorizontalDemo(App):
    def build(self):
        root = ScrollView(do_scroll_x=True, do_scroll_y=False, scroll_type=['bars', 'content'], bar_width=dp(8), bar_color=[0.3, 0.6, 1.0, 0.8])
        row = BoxLayout(orientation='horizontal', size_hint=(None, 1))
        row.bind(minimum_width=row.setter('width'))
        for i in range(50):
            row.add_widget(Button(text=f"Card {i}", size_hint=(None, 1), width=dp(160)))
        root.add_widget(row)

        root.bind(on_scroll_start=lambda *_: print('[horizontal] start')) 
        root.bind(on_scroll_move=lambda *_: print('[horizontal] move'))
        root.bind(on_scroll_stop=lambda *_: print('[horizontal] stop'))
        return root


if __name__ == '__main__':
    HorizontalDemo().run()


