"""
demonstrating nested ScrollViews with parallel horizontal scrolling.
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

from updated_sv import ScrollView
from nested_scrollview_manager import NestedScrollViewManager


class InnerScrollView(ScrollView):
    def __init__(self, panel_index, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = True  # Inner ScrollView scrolls horizontally
        self.do_scroll_y = False
        self.bar_width = dp(6)
        self.scroll_type = ['bars', 'content']
        self.size_hint_x = None
        self.width = dp(300)  # fixed viewport width for the inner scroll
        self.size_hint_y = None  # Don't use size hint for height
        
        # Layout inside the inner scroll - horizontal layout
        content = BoxLayout(orientation='horizontal', size_hint_x=None, size_hint_y=None, padding=dp(8), spacing=dp(6))
        content.bind(minimum_width=content.setter('width'))
        content.bind(minimum_height=content.setter('height'))

        # Add demo labels - enough to make it scrollable horizontally
        for j in range(1, 20):
            label = Label(
                text=f"Item {j}\nPanel {panel_index + 1}",
                size_hint_x=None,
                size_hint_y=None,
                width=dp(100),  # Fixed width for horizontal scrolling
                height=dp(60),  # Fixed height
                color=(0.2, 0.6, 1, 1),  # Blue color to distinguish inner items
                halign='center',
                valign='middle'
            )
            label.bind(size=label.setter('text_size'))  # Set text_size for proper alignment
            content.add_widget(label)

        self.add_widget(content)
        
        # Set a reasonable height for the scrollview
        self.height = dp(80)


class InnerPanel(BoxLayout):
    def __init__(self, panel_index, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_x = None
        self.width = dp(350)  # Fixed width for each panel
        self.size_hint_y = None
        self.height = dp(150)  # total height: header + inner scroll

        # Header row
        header = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(12), 0))
        header.add_widget(Label(
            text=f"Panel {panel_index + 1}",
            bold=True,
            color=(1, 1, 1, 1),  # White text
        ))
        header.add_widget(Label(
            text="Horizontal scroll below",
            color=(0.8, 0.8, 0.8, 1),  # Light gray text
        ))
        self.add_widget(header)

        # Inner horizontal scroll - centered
        scroll_container = BoxLayout(orientation='horizontal')
        scroll_container.add_widget(Label())  # Left spacer
        scroll_container.add_widget(InnerScrollView(panel_index))
        scroll_container.add_widget(Label())  # Right spacer
        self.add_widget(scroll_container)


class TestNestedHorizontalsApp(App):
    def build(self):
        # Create NestedScrollViewManager
        manager = NestedScrollViewManager()
        
        # Outer ScrollView (horizontal)
        outer_scroll = ScrollView(
            do_scroll_x=True,  # Outer ScrollView also scrolls horizontally
            do_scroll_y=False, 
            bar_width=dp(8), 
            scroll_type=['bars', 'content']
        )

        # Vertical container to center the horizontal content
        vertical_container = BoxLayout(orientation='vertical', size_hint_x=None)
        vertical_container.add_widget(Label())  # Top spacer
        
        # Container for panels - horizontal layout
        outer_layout = BoxLayout(orientation='horizontal', size_hint_x=None, size_hint_y=None, height=dp(150), padding=dp(12), spacing=dp(12))
        outer_layout.bind(minimum_width=outer_layout.setter('width'))
        
        vertical_container.add_widget(outer_layout)
        vertical_container.add_widget(Label())  # Bottom spacer
        
        # Bind vertical container width to the horizontal layout width
        outer_layout.bind(width=vertical_container.setter('width'))

        # Add info label at the left
        info_label = Label(
            text="Nested Horizontal ScrollViews Test\n" +
                 "Outer: Horizontal scroll (10 panels)\n" + 
                 "Inner: Horizontal scroll (19 items each)\n" +
                 "Both ScrollViews scroll in the same direction (X-axis)",
            size_hint_x=None,
            width=dp(300),
            size_hint_y=None,
            height=dp(150),
            color=(1, 1, 0, 1),  # Yellow text
            halign='center',
            valign='middle'
        )
        info_label.bind(size=info_label.setter('text_size'))
        outer_layout.add_widget(info_label)

        # Add multiple panels to make the outer scroll scrollable
        for i in range(10):  # Multiple panels to ensure outer scrolling is needed
            panel = InnerPanel(i)
            outer_layout.add_widget(panel)

        outer_scroll.add_widget(vertical_container)
        
        # Add the outer ScrollView to the NestedScrollViewManager
        manager.add_widget(outer_scroll)
        
        return manager


if __name__ == "__main__":
    TestNestedHorizontalsApp().run()
