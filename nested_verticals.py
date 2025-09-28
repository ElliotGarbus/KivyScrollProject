from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp


class InnerScrollView(ScrollView):
    def __init__(self, panel_index, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self.bar_width = dp(6)
        self.scroll_type = ['bars', 'content']
        self.size_hint_y = None
        self.height = dp(200)  # fixed viewport height for the inner scroll
        self.size_hint_x = None  # Don't use size hint for width

        # Layout inside the inner scroll
        content = GridLayout(cols=1, size_hint_y=None, size_hint_x=None, padding=dp(8), spacing=dp(6))
        content.bind(minimum_height=content.setter('height'))
        content.bind(minimum_width=content.setter('width'))

        # Add demo labels
        for j in range(1, 25):
            label = Label(
                text=f"Item {j} in Panel {panel_index + 1}",
                size_hint_y=None,
                size_hint_x=None,  # Don't use size hint for width
                height=dp(32),
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
        ))
        header.add_widget(Label(
            text="Inner scroll area below",
        ))
        self.add_widget(header)

        # Inner vertical scroll - centered
        scroll_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(200))
        scroll_container.add_widget(Label())  # Left spacer
        scroll_container.add_widget(InnerScrollView(panel_index))
        scroll_container.add_widget(Label())  # Right spacer
        self.add_widget(scroll_container)


class NestedScrollsApp(App):
    def build(self):
        # Outer ScrollView
        outer_scroll = ScrollView(do_scroll_x=False, bar_width=dp(8), scroll_type=['bars', 'content'])

        # Container for panels
        outer_layout = GridLayout(cols=1, size_hint_y=None, padding=dp(12), spacing=dp(12))
        outer_layout.bind(minimum_height=outer_layout.setter('height'))

        # Add 10 panels
        for i in range(10):
            outer_layout.add_widget(InnerPanel(i))

        outer_scroll.add_widget(outer_layout)
        return outer_scroll


if __name__ == "__main__":
    NestedScrollsApp().run()
