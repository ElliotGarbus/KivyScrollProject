"""
Hybrid KV/Python example of nested orthogonal ScrollViews for documentation.

This example demonstrates:
- KV rules defining widget templates
- Python code dynamically creating content
- Proper use of NestedScrollViewManager
- Realistic pattern for data-driven nested ScrollViews
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from updated_sv import ScrollView
from kivy.properties import NumericProperty

from kivy.factory import Factory
from nested_scrollview_manager import NestedScrollViewManager

# Register custom widgets with Factory so KV can use them
Factory.register('NestedScrollViewManager', cls=NestedScrollViewManager)

# Unregister the original ScrollView and register our updated version
Factory.unregister('ScrollView')
Factory.register('ScrollView', cls=ScrollView)


KV = '''
<HorizontalScrollRow>:
    do_scroll_x: True
    do_scroll_y: False
    size_hint_y: None
    height: 120
    smooth_scroll_end: 10
    bar_width: '10dp'
    scroll_type: ['bars', 'content']
    
    BoxLayout:
        id: content_layout
        orientation: 'horizontal'
        size_hint_x: None
        size: self.minimum_width, dp(80)
        spacing: 10

NestedScrollViewManager:
    ScrollView:
        id: outer_scroll
        do_scroll_x: False
        do_scroll_y: True
        smooth_scroll_end: 10
        bar_width: '10dp'
        scroll_type: ['bars', 'content']
        
        BoxLayout:
            id: outer_layout
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: 20
'''

class HorizontalScrollRow(ScrollView):
    row_number = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(10):
            btn = Button(
                text=f'Button {self.row_number}-{i}',
                size_hint_x=None,
                width='100dp'
            )
            self.ids.content_layout.add_widget(btn)


class NestedScrollKVApp(App):
    def build(self):
        return Builder.load_string(KV)
        
    def on_start(self):
        # Dynamically create 5 horizontal ScrollViews with buttons
        for i in range(10):
            # Create a horizontal ScrollView using the KV rule
            h_scroll = HorizontalScrollRow(row_number=i)
            # Get the content layout
            self.root.ids.outer_layout.add_widget(h_scroll)
        

if __name__ == '__main__':
    NestedScrollKVApp().run()

