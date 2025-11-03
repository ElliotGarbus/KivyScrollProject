"""
KV-based Nested Parallel Vertical ScrollView Demo
==================================================
Demonstrating nested ScrollViews with parallel scrolling using KV language.
Nested Parallel Vertical Scrolling - both outer and inner ScrollViews scroll vertically.

This demonstrates the same functionality as demo_nested_verticals.py but uses KV language
for the layout definition.
"""

# CRITICAL: Register custom ScrollView with Factory BEFORE using it in KV
from kivy.factory import Factory
import scrollview

# Unregister the default ScrollView and register our custom one
Factory.unregister('ScrollView')
Factory.register('ScrollView', cls=scrollview.ScrollView)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty

# KV string defining the layout structure
kv = '''
<InnerPanel>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(260)
    
    # Header row
    BoxLayout:
        size_hint_y: None
        height: dp(44)
        padding: dp(12), 0
        
        Label:
            text: f'Panel {root.panel_index + 1}'
            bold: True
            color: 1, 1, 1, 1
        
        Label:
            text: 'Vertical inner scroll below'
            color: 0.8, 0.8, 0.8, 1
    
    # Inner vertical scroll - centered with spacers
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(200)
        
        Label:  # Left spacer
        
        ScrollView:
            id: inner_scroll
            do_scroll_x: False
            do_scroll_y: True
            bar_width: dp(6)
            scroll_type: ['bars', 'content']
            size_hint_y: None
            size_hint_x: None
            height: dp(200)
            
            GridLayout:
                id: content
                cols: 1
                size_hint_y: None
                size_hint_x: None
                height: self.minimum_height
                width: self.minimum_width
                padding: dp(8)
                spacing: dp(6)
        
        Label:  # Right spacer

# Main layout
ScrollView:
    do_scroll_x: False
    do_scroll_y: True
    bar_width: dp(8)
    scroll_type: ['bars', 'content']
    
    GridLayout:
        id: outer_layout
        cols: 1
        size_hint_y: None
        height: self.minimum_height
        padding: dp(12)
        spacing: dp(12)
        
        # Info label at the top
        Label:
            text: 'Nested Vertical ScrollViews Test\\nOuter: Vertical scroll (15 panels)\\nInner: Vertical scroll (30 items each)\\nBoth ScrollViews scroll in the same direction (Y-axis)'
            size_hint_y: None
            height: dp(80)
            color: 1, 1, 0, 1
            halign: 'center'
            text_size: self.size
'''


class InnerPanel(BoxLayout):
    """Panel widget containing a vertical ScrollView with items."""
    panel_index = NumericProperty(0)
    
    def on_kv_post(self, base_widget):
        """Populate the inner scroll content after KV is processed."""
        content = self.ids.content
        scrollview = self.ids.inner_scroll
        
        # Add 30 labels to make it scrollable
        for j in range(1, 31):
            label = Label(
                text=f"Inner Item {j} in Panel {self.panel_index + 1}",
                size_hint_y=None,
                size_hint_x=None,
                height='32dp',
                color=(0.2, 0.6, 1, 1),  # Blue color to distinguish inner items
            )
            # Size label to fit text
            label.bind(texture_size=label.setter('size'))
            content.add_widget(label)
        
        # Bind scrollview width to content width so it centers properly
        content.bind(width=scrollview.setter('width'))


class NestedVerticalsKVDemo(App):
    """Main application."""
    
    def build(self):
        root = Builder.load_string(kv)
        
        # Get the outer layout container
        outer_layout = root.ids.outer_layout
        
        # Add 15 panels to make the outer scroll scrollable
        for i in range(15):
            panel = InnerPanel(panel_index=i)
            outer_layout.add_widget(panel)
        
        return root


if __name__ == '__main__':
    NestedVerticalsKVDemo().run()

