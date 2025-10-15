"""
demonstrating nested ScrollViews with parallel scrolling.
Nested Parallel Vertical Scrolling
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

from updated_sv_no_manager import ScrollView


class InnerScrollView(ScrollView):
    def __init__(self, panel_index, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True  # Inner ScrollView scrolls vertically
        self.bar_width = dp(6)
        self.scroll_type = ['bars', 'content']
        self.size_hint_y = None
        self.height = dp(200)  # fixed viewport height for the inner scroll
        self.size_hint_x = None  # Don't use size hint for width
        
        # Layout inside the inner scroll
        content = GridLayout(cols=1, size_hint_y=None, size_hint_x=None, padding=dp(8), spacing=dp(6))
        content.bind(minimum_height=content.setter('height'))
        content.bind(minimum_width=content.setter('width'))

        # Add demo labels - enough to make it scrollable
        for j in range(1, 30):
            label = Label(
                text=f"Inner Item {j} in Panel {panel_index + 1}",
                size_hint_y=None,
                size_hint_x=None,  # Don't use size hint for width
                height=dp(32),
                color=(0.2, 0.6, 1, 1),  # Blue color to distinguish inner items
            )
            label.bind(texture_size=label.setter('size'))  # Size to fit text
            content.add_widget(label)

        self.add_widget(content)
        
        # Bind scrollview width to content width
        content.bind(width=self.setter('width'))


class InnerPanel(BoxLayout):
    def __init__(self, panel_index, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(260)  # total height: header + inner scroll

        # Header row
        header = BoxLayout(size_hint_y=None, height=dp(44), padding=(dp(12), 0))
        header.add_widget(Label(
            text=f"Panel {panel_index + 1}",
            bold=True,
            color=(1, 1, 1, 1),  # White text
        ))
        header.add_widget(Label(
            text="Vertical inner scroll below",
            color=(0.8, 0.8, 0.8, 1),  # Light gray text
        ))
        self.add_widget(header)

        # Inner vertical scroll - centered
        scroll_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(200))
        scroll_container.add_widget(Label())  # Left spacer
        scroll_container.add_widget(InnerScrollView(panel_index))
        scroll_container.add_widget(Label())  # Right spacer
        self.add_widget(scroll_container)


class TestNestedVerticalsApp(App):
    def build(self):
        # Outer ScrollView (also vertical)
        outer_scroll = ScrollView(
            do_scroll_x=False, 
            do_scroll_y=True,  # Outer ScrollView also scrolls vertically
            bar_width=dp(8), 
            scroll_type=['bars', 'content']
        )

        # Container for panels
        outer_layout = GridLayout(cols=1, size_hint_y=None, padding=dp(12), spacing=dp(12))
        outer_layout.bind(minimum_height=outer_layout.setter('height'))

        # Add multiple panels to make the outer scroll scrollable
        for i in range(15):  # More panels to ensure outer scrolling is needed
            panel = InnerPanel(i)
            outer_layout.add_widget(panel)

        # Add info label at the top
        info_label = Label(
            text="Nested Vertical ScrollViews Test\n" +
                 "Outer: Vertical scroll (15 panels)\n" + 
                 "Inner: Vertical scroll (30 items each)\n" +
                 "Both ScrollViews scroll in the same direction (Y-axis)",
            size_hint_y=None,
            height=dp(80),
            color=(1, 1, 0, 1),  # Yellow text
            halign='center'
        )
        info_label.bind(size=info_label.setter('text_size'))
        outer_layout.add_widget(info_label)

        outer_scroll.add_widget(outer_layout)
        
        return outer_scroll


if __name__ == "__main__":
    TestNestedVerticalsApp().run()
