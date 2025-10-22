"""
Test for 3-level nested vertical ScrollViews.

This is the first test for arbitrary depth nesting support.
Tests simple chain delegation: Outer -> Middle -> Inner (all vertical)

Expected behavior:
- Touch starts at innermost level
- When inner reaches boundary, delegates to middle
- When middle reaches boundary, delegates to outer
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

from scrollview import ScrollView


class InnermostScrollView(ScrollView):
    """Level 3 (deepest): Simple vertical scroll with items"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.bar_width = dp(4)
        self.scroll_type = ['bars', 'content']
        self.size_hint_y = None
        self.height = dp(150)
        
        # Content
        content = GridLayout(cols=1, size_hint_y=None, padding=dp(4), spacing=dp(4))
        content.bind(minimum_height=content.setter('height'))
        
        # Add items
        for i in range(1, 20):
            label = Label(
                text=f"Innermost Item {i}",
                size_hint_y=None,
                height=dp(28),
                color=(0.2, 1, 0.2, 1),  # Green
            )
            content.add_widget(label)
        
        self.add_widget(content)


class MiddleScrollView(ScrollView):
    """Level 2 (middle): Vertical scroll containing innermost ScrollView"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.bar_width = dp(5)
        self.scroll_type = ['bars', 'content']
        self.size_hint_y = None
        self.height = dp(300)
        
        # Content
        content = GridLayout(cols=1, size_hint_y=None, padding=dp(8), spacing=dp(8))
        content.bind(minimum_height=content.setter('height'))
        
        # Add some items before innermost scroll
        for i in range(1, 4):
            label = Label(
                text=f"Middle Item {i}",
                size_hint_y=None,
                height=dp(32),
                color=(0.2, 0.6, 1, 1),  # Blue
            )
            content.add_widget(label)
        
        # Add innermost scroll
        innermost = InnermostScrollView()
        content.add_widget(innermost)
        
        # Add some items after innermost scroll
        for i in range(4, 8):
            label = Label(
                text=f"Middle Item {i}",
                size_hint_y=None,
                height=dp(32),
                color=(0.2, 0.6, 1, 1),  # Blue
            )
            content.add_widget(label)
        
        self.add_widget(content)


class OuterScrollView(ScrollView):
    """Level 1 (outer): Vertical scroll containing middle ScrollView"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.bar_width = dp(8)
        self.scroll_type = ['bars', 'content']
        
        # Content
        content = GridLayout(cols=1, size_hint_y=None, padding=dp(12), spacing=dp(12))
        content.bind(minimum_height=content.setter('height'))
        
        # Info label
        info = Label(
            text="3-LEVEL NESTED VERTICAL TEST\n" +
                 "Outer (red) -> Middle (blue) -> Inner (green)\n" +
                 "All scroll vertically (parallel chain)\n\n" +
                 "Test: Scroll in innermost, should chain to middle, then outer",
            size_hint_y=None,
            height=dp(100),
            color=(1, 1, 0, 1),  # Yellow
            halign='center'
        )
        info.bind(size=info.setter('text_size'))
        content.add_widget(info)
        
        # Add items before middle scroll
        for i in range(1, 4):
            label = Label(
                text=f"Outer Item {i}",
                size_hint_y=None,
                height=dp(40),
                color=(1, 0.3, 0.3, 1),  # Red
            )
            content.add_widget(label)
        
        # Add middle scroll
        middle = MiddleScrollView()
        content.add_widget(middle)
        
        # Add items after middle scroll
        for i in range(4, 10):
            label = Label(
                text=f"Outer Item {i}",
                size_hint_y=None,
                height=dp(40),
                color=(1, 0.3, 0.3, 1),  # Red
            )
            content.add_widget(label)
        
        self.add_widget(content)


class Test3LevelVerticalApp(App):
    def build(self):
        return OuterScrollView()


if __name__ == "__main__":
    Test3LevelVerticalApp().run()

