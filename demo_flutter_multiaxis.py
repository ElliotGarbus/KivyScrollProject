"""
Flutter Effect Multi-Axis Demo
================================

Demonstrates the FlutterScrollEffect working in three different configurations:
- TOP LEFT: Vertical scrolling only (Y axis)
- TOP RIGHT: Horizontal scrolling only (X axis)  
- BOTTOM: XY scrolling (both axes)

All three use the same FlutterScrollEffect with automatic axis detection.
The rubber band resistance will scale properly with each viewport dimension.

Try scrolling past the edges in each view to see the iOS-style rubber band effect!
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from flutter_scroll_effect import FlutterScrollEffect

# Register the effect so KV can use it
Factory.register('FlutterScrollEffect', cls=FlutterScrollEffect)

# KV language for the UI
kv = '''
BoxLayout:
    orientation: 'vertical'
    spacing: dp(5)
    padding: dp(10)
    
    # Top row - Vertical and Horizontal
    BoxLayout:
        orientation: 'horizontal'
        spacing: dp(5)
        size_hint_y: 0.5
        
        # Vertical ScrollView (LEFT)
        BoxLayout:
            orientation: 'vertical'
            
            Label:
                size_hint_y: None
                height: dp(35)
                text: 'VERTICAL SCROLLING'
                font_size: '13sp'
                bold: True
                color: 0.3, 0.8, 1.0, 1
                canvas.before:
                    Color:
                        rgba: 0.15, 0.15, 0.2, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
            
            ScrollView:
                id: vertical_scroll
                do_scroll_x: False
                do_scroll_y: True
                scroll_type: ['bars', 'content']
                bar_width: dp(8)
                bar_color: 0.3, 0.8, 1.0, 0.8
                effect_cls: 'FlutterScrollEffect'
                
                BoxLayout:
                    id: vertical_content
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(10)
                    spacing: dp(5)
        
        # Horizontal ScrollView (RIGHT)
        BoxLayout:
            orientation: 'vertical'
            
            Label:
                size_hint_y: None
                height: dp(35)
                text: 'HORIZONTAL SCROLLING'
                font_size: '13sp'
                bold: True
                color: 1.0, 0.8, 0.3, 1
                canvas.before:
                    Color:
                        rgba: 0.2, 0.15, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
            
            ScrollView:
                id: horizontal_scroll
                do_scroll_x: True
                do_scroll_y: False
                scroll_type: ['bars', 'content']
                bar_width: dp(8)
                bar_color: 1.0, 0.8, 0.3, 0.8
                effect_cls: 'FlutterScrollEffect'
                
                BoxLayout:
                    id: horizontal_content
                    orientation: 'horizontal'
                    size_hint_x: None
                    width: self.minimum_width
                    padding: dp(10)
                    spacing: dp(5)
    
    # Bottom row - XY ScrollView
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.5
        
        Label:
            size_hint_y: None
            height: dp(35)
            text: 'XY SCROLLING (Both Axes)'
            font_size: '13sp'
            bold: True
            color: 0.3, 1.0, 0.5, 1
            canvas.before:
                Color:
                    rgba: 0.1, 0.2, 0.15, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
        
        ScrollView:
            id: xy_scroll
            do_scroll_x: True
            do_scroll_y: True
            scroll_type: ['bars', 'content']
            bar_width: dp(8)
            bar_color: 0.3, 1.0, 0.5, 0.8
            effect_cls: 'FlutterScrollEffect'
            
            FloatLayout:
                id: xy_content
                size_hint: None, None
                size: dp(1200), dp(800)
'''


class ColoredLabel(Label):
    '''A label with a colored background.'''
    def __init__(self, text, bg_color=(0.2, 0.2, 0.25, 1), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = '12sp'
        self.padding = (10, 10)
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class FlutterMultiAxisDemo(App):
    def build(self):
        root = Builder.load_string(kv)
        
        # Populate the three different scroll views
        self._populate_vertical(root.ids.vertical_content)
        self._populate_horizontal(root.ids.horizontal_content)
        self._populate_xy(root.ids.xy_content)
        
        # Print effect info
        self._print_effect_info(root)
        
        return root
    
    def _populate_vertical(self, container):
        '''Populate vertical scrollview with content.'''
        colors = [
            (0.2, 0.3, 0.5, 1),
            (0.3, 0.2, 0.5, 1),
            (0.2, 0.5, 0.3, 1),
            (0.5, 0.3, 0.2, 1),
        ]
        
        # Header
        header = ColoredLabel(
            '[b]VERTICAL SCROLL TEST[/b]\n'
            'Scroll up and down. Try flinging past the edges!',
            bg_color=(0.15, 0.25, 0.4, 1)
        )
        header.markup = True
        header.size_hint_y = None
        header.height = 70
        container.add_widget(header)
        
        # Add 30 items
        for i in range(1, 31):
            label = ColoredLabel(
                f'[b]Item {i}[/b] - Vertical scroll content. ',
                bg_color=colors[i % len(colors)]
            )
            label.markup = True
            label.size_hint_y = None
            label.height = 50
            container.add_widget(label)
        
        # Footer
        footer = ColoredLabel(
            '[b]END OF VERTICAL CONTENT[/b]\n'
            'Scroll back to the top!',
            bg_color=(0.15, 0.25, 0.4, 1)
        )
        footer.markup = True
        footer.size_hint_y = None
        footer.height = 70
        container.add_widget(footer)
    
    def _populate_horizontal(self, container):
        '''Populate horizontal scrollview with content.'''
        colors = [
            (0.5, 0.3, 0.2, 1),
            (0.5, 0.4, 0.2, 1),
            (0.5, 0.5, 0.2, 1),
            (0.4, 0.5, 0.2, 1),
        ]
        
        # Add horizontal items
        for i in range(1, 21):
            label = ColoredLabel(
                f'[b]Card {i}[/b]\n\n'
                f'Horizontal\nscroll item\n\n'
                f'Fling past\nleft/right edges!',
                bg_color=colors[i % len(colors)]
            )
            label.markup = True
            label.size_hint_x = None
            label.width = 120
            label.halign = 'center'
            label.valign = 'middle'
            label.text_size = (110, None)
            container.add_widget(label)
    
    def _populate_xy(self, container):
        '''Populate XY scrollview with a grid of positioned items.'''
        from kivy.graphics import Color, Rectangle, Line
        
        # Draw a grid background
        with container.canvas.before:
            Color(0.1, 0.15, 0.12, 1)
            Rectangle(pos=(0, 0), size=container.size)
            
            # Grid lines
            Color(0.2, 0.3, 0.25, 0.3)
            for x in range(0, int(container.width), 100):
                Line(points=[x, 0, x, container.height], width=1)
            for y in range(0, int(container.height), 100):
                Line(points=[0, y, container.width, y], width=1)
        
        colors = [
            (0.8, 0.3, 0.3, 1),
            (0.3, 0.8, 0.3, 1),
            (0.3, 0.3, 0.8, 1),
            (0.8, 0.8, 0.3, 1),
            (0.8, 0.3, 0.8, 1),
            (0.3, 0.8, 0.8, 1),
        ]
        
        # Add items at various positions
        positions = [
            (50, 50), (250, 50), (450, 50), (650, 50), (850, 50),
            (50, 200), (250, 200), (450, 200), (650, 200), (850, 200),
            (50, 350), (250, 350), (450, 350), (650, 350), (850, 350),
            (50, 500), (250, 500), (450, 500), (650, 500), (850, 500),
        ]
        
        for i, (x, y) in enumerate(positions):
            label = ColoredLabel(
                f'[b]Item {i+1}[/b]\n'
                f'Position:\n({x}, {y})\n\n'
                f'Scroll in\nany direction!',
                bg_color=colors[i % len(colors)]
            )
            label.markup = True
            label.size_hint = (None, None)
            label.size = (150, 120)
            label.pos = (x, y)
            label.halign = 'center'
            label.valign = 'middle'
            label.text_size = (140, None)
            container.add_widget(label)
        
        # Add corner markers
        corners = [
            (10, 10, "BOTTOM LEFT"),
            (container.width - 160, 10, "BOTTOM RIGHT"),
            (10, container.height - 60, "TOP LEFT"),
            (container.width - 160, container.height - 60, "TOP RIGHT"),
        ]
        
        for x, y, text in corners:
            label = ColoredLabel(
                f'[b]{text}[/b]\nCorner',
                bg_color=(0.5, 0.5, 0.5, 1)
            )
            label.markup = True
            label.size_hint = (None, None)
            label.size = (150, 50)
            label.pos = (x, y)
            label.halign = 'center'
            label.valign = 'middle'
            label.text_size = (140, None)
            container.add_widget(label)
    
    def _print_effect_info(self, root):
        '''Print information about the effects to console.'''
        print("\n" + "="*70)
        print("FLUTTER SCROLL EFFECT - MULTI-AXIS DEMO")
        print("="*70)
        
        sv_vertical = root.ids.vertical_scroll
        sv_horizontal = root.ids.horizontal_scroll
        sv_xy = root.ids.xy_scroll
        
        print("\nVERTICAL SCROLLVIEW:")
        print(f"  - do_scroll_x: {sv_vertical.do_scroll_x}")
        print(f"  - do_scroll_y: {sv_vertical.do_scroll_y}")
        print(f"  - effect_x: {type(sv_vertical.effect_x).__name__}")
        print(f"  - effect_y: {type(sv_vertical.effect_y).__name__}")
        
        print("\nHORIZONTAL SCROLLVIEW:")
        print(f"  - do_scroll_x: {sv_horizontal.do_scroll_x}")
        print(f"  - do_scroll_y: {sv_horizontal.do_scroll_y}")
        print(f"  - effect_x: {type(sv_horizontal.effect_x).__name__}")
        print(f"  - effect_y: {type(sv_horizontal.effect_y).__name__}")
        
        print("\nXY SCROLLVIEW:")
        print(f"  - do_scroll_x: {sv_xy.do_scroll_x}")
        print(f"  - do_scroll_y: {sv_xy.do_scroll_y}")
        print(f"  - effect_x: {type(sv_xy.effect_x).__name__}")
        print(f"  - effect_y: {type(sv_xy.effect_y).__name__}")
        
        print("\nFLUTTER EFFECT PARAMETERS:")
        effect = sv_vertical.effect_y
        print(f"  - rubber_band_coeff: {effect.rubber_band_coeff}")
        print(f"  - spring_stiffness: {effect.spring_stiffness}")
        print(f"  - spring_mass: {effect.spring_mass}")
        
        from math import sqrt
        critical_damping = 2.0 * sqrt(effect.spring_stiffness * effect.spring_mass)
        print(f"  - critical_damping (calculated): {critical_damping:.2f}")
        
        print("\nTEST INSTRUCTIONS:")
        print("  1. VERTICAL (top-left): Scroll up/down, fling past edges")
        print("  2. HORIZONTAL (top-right): Scroll left/right, fling past edges")
        print("  3. XY (bottom): Scroll in any direction, test all edges")
        print("  4. Each axis should have proper rubber band resistance")
        print("  5. No oscillation - smooth bounce back")
        print("="*70 + "\n")


if __name__ == '__main__':
    FlutterMultiAxisDemo().run()

