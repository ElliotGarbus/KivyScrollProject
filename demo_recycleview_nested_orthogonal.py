"""
Nested RecycleView Demo - Orthogonal Configuration
===================================================
Demonstrates nested RecycleViews using the custom ScrollView:
- Outer: Horizontal RecycleView with 20 panels
- Inner: Each panel contains a vertical RecycleView with 50 buttons

This tests whether the custom ScrollView correctly handles RecycleView's
internal scrolling in an orthogonal nested configuration.
"""

# CRITICAL: Monkey patch ScrollView BEFORE RecycleView imports it
# RecycleView does "from kivy.uix.scrollview import ScrollView"
# So we need to replace ScrollView in that module before RecycleView loads

import kivy.uix.scrollview
import scrollview

# Replace ScrollView in the kivy.uix.scrollview module
kivy.uix.scrollview.ScrollView = scrollview.ScrollView

# Also register with Factory for kv language
from kivy.factory import Factory
Factory.unregister('ScrollView')
Factory.register('ScrollView', cls=scrollview.ScrollView)

# NOW we can import RecycleView - it will import our custom ScrollView
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

kv = '''
#:import dp kivy.metrics.dp

# Button widget for inner vertical RecycleViews
<ItemButton@Button>:
    size_hint_y: None
    height: dp(50)
    background_color: 0.2, 0.6, 0.8, 1
    on_release: print(f'Button pressed: {self.text}')

# Panel container - holds a vertical RecycleView
<PanelContainer>:
    orientation: 'vertical'
    size_hint_x: None
    width: dp(300)
    canvas.before:
        Color:
            rgba: 0.15, 0.15, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    # Header label
    Label:
        text: f'Panel {root.panel_index}'
        size_hint_y: None
        height: dp(40)
        bold: True
        font_size: '18sp'
        color: 1, 1, 1, 1
    
    # Inner vertical RecycleView with 50 buttons
    RecycleView:
        id: inner_rv
        viewclass: 'ItemButton'
        scroll_type: ['bars', 'content']
        bar_width: dp(10)
        do_scroll_x: False
        do_scroll_y: True
        
        RecycleBoxLayout:
            default_size: None, dp(50)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(2)

# Main layout
BoxLayout:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)
    
    # Instructions
    Label:
        text: 'Outer: Horizontal RecycleView (20 panels)\\nInner: Vertical RecycleView (50 items each)'
        size_hint_y: None
        height: dp(60)
        font_size: '14sp'
    
    # Outer horizontal RecycleView
    RecycleView:
        id: outer_rv
        viewclass: 'PanelContainer'
        scroll_type: ['bars', 'content']
        bar_width: dp(10)
        do_scroll_x: True
        do_scroll_y: False
        
        RecycleBoxLayout:
            default_size: dp(300), None
            default_size_hint: None, 1
            size_hint: None, 1
            width: self.minimum_width
            orientation: 'horizontal'
            spacing: dp(10)
'''


class PanelContainer(BoxLayout):
    """Container for each panel with its own vertical RecycleView."""
    panel_index = StringProperty('0')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        inner_rv = self.ids.get('inner_rv')
        if inner_rv and not inner_rv.data:
            inner_rv.data = [
                {'text': f'Panel {self.panel_index} - Item {i}'}
                for i in range(50)
            ]


class RecycleViewNestedDemo(App):
    """Main application."""
    
    def build(self):
        root = Builder.load_string(kv)
        
        # Populate outer RecycleView with 20 panels
        outer_rv = root.ids.outer_rv
        outer_rv.data = [{'panel_index': str(i)} for i in range(20)]
        
        return root


if __name__ == '__main__':
    RecycleViewNestedDemo().run()
