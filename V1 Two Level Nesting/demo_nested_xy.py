"""
Demonstrating nested ScrollViews with XY (both horizontal and vertical) scrolling.
A matrix of inner XY ScrollViews nested inside an outer XY ScrollView.
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

from scrollview import ScrollView


class InnerScrollView(ScrollView):
    def __init__(self, row, col, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = True  # Inner ScrollView scrolls both X and Y
        self.do_scroll_y = True
        self.bar_width = dp(10)
        self.scroll_type = ['bars', 'content']
        self.size_hint = (None, None)
        self.size = (dp(300), dp(250))  # Fixed size viewport
        
        # Grid layout inside the inner scroll - scrollable in both directions
        content = GridLayout(
            cols=5, 
            size_hint=(None, None), 
            padding=dp(8), 
            spacing=dp(6)
        )
        content.bind(minimum_height=content.setter('height'))
        content.bind(minimum_width=content.setter('width'))

        # Add a grid of buttons to make it scrollable in both directions
        for i in range(12):  # 12 rows
            for j in range(8):  # 8 columns (5 visible at a time)
                btn = Button(
                    text=f"[{row},{col}]\nBtn {i},{j}",
                    size_hint=(None, None),
                    size=(dp(90), dp(60)),
                    background_color=(0.2 + (i * 0.05), 0.4 + (j * 0.05), 0.8, 1)
                )
                content.add_widget(btn)

        self.add_widget(content)


class InnerPanel(BoxLayout):
    def __init__(self, row, col, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (dp(320), dp(310))  # Total size: header + inner scroll + padding

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(8), dp(4)))
        header.add_widget(Label(
            text=f"Panel [{row}, {col}]",
            bold=True,
            color=(1, 1, 0, 1),  # Yellow text
            size_hint_x=0.4
        ))
        header.add_widget(Label(
            text="XY Scroll",
            color=(0.8, 0.8, 0.8, 1),
            size_hint_x=0.6
        ))
        self.add_widget(header)

        # Inner XY scroll
        scroll_container = BoxLayout(size_hint=(1, 1), padding=dp(10))
        scroll_container.add_widget(InnerScrollView(row, col))
        self.add_widget(scroll_container)


class TestNestedXYApp(App):
    def build(self):
        # Outer ScrollView (XY scrolling)
        outer_scroll = ScrollView(
            do_scroll_x=True,  # Outer ScrollView scrolls both X and Y
            do_scroll_y=True,
            bar_width=dp(10), 
            scroll_type=['bars', 'content']
        )

        # Container for the matrix of panels
        outer_layout = BoxLayout(orientation='vertical', size_hint=(None, None), padding=dp(12), spacing=dp(12))
        outer_layout.bind(minimum_height=outer_layout.setter('height'))
        outer_layout.bind(minimum_width=outer_layout.setter('width'))

        # Add info label at the top
        info_label = Label(
            text="Nested XY (Both Axes) ScrollViews Test\n" +
                 "Outer: XY scroll (3x4 matrix of panels)\n" + 
                 "Inner: XY scroll (12x8 grid of buttons each)\n" +
                 "All ScrollViews scroll in both X and Y directions",
            size_hint=(None, None),
            size=(dp(1000), dp(100)),
            color=(0, 1, 1, 1),  # Cyan text
            halign='left',
            valign='top'
        )
        info_label.bind(size=info_label.setter('text_size'))
        outer_layout.add_widget(info_label)

        # Create a matrix of panels (3 rows x 4 columns)
        for row in range(3):
            row_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), spacing=dp(12))
            row_layout.bind(minimum_width=row_layout.setter('width'))
            row_layout.bind(minimum_height=row_layout.setter('height'))
            
            for col in range(4):
                panel = InnerPanel(row, col)
                row_layout.add_widget(panel)
            
            outer_layout.add_widget(row_layout)

        outer_scroll.add_widget(outer_layout)
        
        return outer_scroll


if __name__ == "__main__":
    TestNestedXYApp().run()

