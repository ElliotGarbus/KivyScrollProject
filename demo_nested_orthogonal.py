"""
Interactive nested demo
Demo showing nested scrollviews without a manager.
Test orthogonal nested scrollview (Vertical outer + Horizontal inner, Horizontal outer + Vertical inner)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from scrollview import ScrollView


class NestedScrollViewDemo(App):
    def build(self):
        main_layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)

        # LEFT SIDE: Vertical outer with horizontal inner scrollviews
        left_vertical_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        left_container = BoxLayout(
            orientation='vertical',
            spacing='20dp',
            size_hint_y=None
        )
        left_container.bind(minimum_height=left_container.setter('height'))
        for i in range(8):
            horizontal_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint_y=None,
                height=dp(120),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8],
                smooth_scroll_end=10
            )
            horizontal_content = BoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_x=None
            )
            horizontal_content.bind(minimum_width=horizontal_content.setter('width'))
            label = Label(
                text=f'Row {i+1} - Horizontal Scroll',
                size_hint_x=None,
                width=dp(200),
                height=dp(30),
                color=[1, 1, 1, 1],
                bold=True
            )
            horizontal_content.add_widget(label)
            for j in range(15):
                btn = Button(
                    text=f'Btn {j+1}',
                    size_hint_x=None,
                    width=dp(100),
                    height=dp(80),
                    background_color=[0.2 + (i * 0.1) % 0.8, 0.3, 0.7, 1]
                )
                horizontal_content.add_widget(btn)
            horizontal_sv.add_widget(horizontal_content)
            left_container.add_widget(horizontal_sv)
        left_vertical_sv.add_widget(left_container)
        main_layout.add_widget(left_vertical_sv)

        # RIGHT SIDE: Horizontal outer with vertical inner scrollviews
        right_horizontal_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.6, 0.8],
            smooth_scroll_end=10
        )
        right_container = BoxLayout(
            orientation='horizontal',
            spacing='20dp',
            size_hint_x=None
        )
        right_container.bind(minimum_width=right_container.setter('width'))
        for i in range(6):
            vertical_sv = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint_x=None,
                width=dp(200),
                bar_width=dp(6),
                bar_color=[1.0, 0.3, 0.5, 0.8],
                smooth_scroll_end=10
            )
            vertical_content = GridLayout(
                cols=1,
                spacing=dp(10),
                size_hint_y=None,
                height=0
            )
            vertical_content.bind(minimum_height=vertical_content.setter('height'))
            label = Label(
                text=f'Column {i+1}\nVertical Scroll',
                size_hint_y=None,
                height=dp(40),
                color=[1, 1, 1, 1],
                bold=True
            )
            vertical_content.add_widget(label)
            for j in range(20):
                btn = Button(
                    text=f'Item {j+1}',
                    size_hint_y=None,
                    height=dp(60),
                    background_color=[0.7, 0.3, 0.2 + (i * 0.1) % 0.8, 1]
                )
                vertical_content.add_widget(btn)
            vertical_sv.add_widget(vertical_content)
            right_container.add_widget(vertical_sv)
        right_horizontal_sv.add_widget(right_container)
        main_layout.add_widget(right_horizontal_sv)

        return main_layout


if __name__ == '__main__':
    NestedScrollViewDemo().run()


