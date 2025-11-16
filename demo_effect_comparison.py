"""
Scroll Effect Comparison Demo
==============================

This demo shows two ScrollViews side-by-side:
- LEFT: Kivy's default DampedScrollEffect (can oscillate)
- RIGHT: Flutter-inspired effect (critically damped, stable)

Try scrolling to the edge and releasing to see the difference:
- The left side may oscillate/bounce repeatedly
- The right side will smoothly return without oscillation

Instructions:
- Scroll each view to the top or bottom edge
- Fling it past the edge with velocity
- Observe the bounce-back behavior
- The Flutter effect should feel more stable and iOS-like
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.effects.dampedscroll import DampedScrollEffect
from flutter_scroll_effect import FlutterScrollEffect

# KV language for the UI
kv = '''
BoxLayout:
    orientation: 'horizontal'
    spacing: dp(2)
    padding: dp(10)
    
    # Left side - Kivy Default (DampedScrollEffect)
    BoxLayout:
        orientation: 'vertical'
        
        Label:
            size_hint_y: None
            height: dp(40)
            text: 'KIVY DEFAULT\\n(DampedScrollEffect)'
            font_size: '14sp'
            bold: True
            color: 1, 0.3, 0.3, 1
            canvas.before:
                Color:
                    rgba: 0.2, 0.2, 0.2, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
        
        ScrollView:
            id: kivy_scroll
            do_scroll_x: False
            do_scroll_y: True
            scroll_type: ['bars', 'content']
            bar_width: dp(10)
            bar_color: 1, 0.3, 0.3, 0.8
            effect_cls: 'DampedScrollEffect'
            
            BoxLayout:
                id: kivy_content
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(15)
                spacing: dp(10)
    
    # Divider
    Widget:
        size_hint_x: None
        width: dp(2)
        canvas:
            Color:
                rgba: 0.5, 0.5, 0.5, 1
            Rectangle:
                pos: self.pos
                size: self.size
    
    # Right side - Flutter-inspired
    BoxLayout:
        orientation: 'vertical'
        
        Label:
            size_hint_y: None
            height: dp(40)
            text: 'FLUTTER-INSPIRED\\n(Critical Damping)'
            font_size: '14sp'
            bold: True
            color: 0.3, 1, 0.3, 1
            canvas.before:
                Color:
                    rgba: 0.2, 0.2, 0.2, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
        
        ScrollView:
            id: flutter_scroll
            do_scroll_x: False
            do_scroll_y: True
            scroll_type: ['bars', 'content']
            bar_width: dp(10)
            bar_color: 0.3, 1, 0.3, 0.8
            effect_cls: 'FlutterScrollEffect'
            
            BoxLayout:
                id: flutter_content
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(15)
                spacing: dp(10)
'''


class ComparisonLabel(Label):
    '''A styled label for the comparison demo.'''
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint_y = None
        self.height = 60
        self.text_size = (None, None)
        self.bind(texture_size=self._update_height)
        self.padding = (10, 10)
        self.halign = 'left'
        self.valign = 'top'
        
    def _update_height(self, *args):
        self.height = max(60, self.texture_size[1] + 20)


class EffectComparisonDemo(App):
    def build(self):
        # Register the FlutterScrollEffect so KV can use it
        Factory.register('FlutterScrollEffect', cls=FlutterScrollEffect)
        Factory.register('DampedScrollEffect', cls=DampedScrollEffect)
        
        root = Builder.load_string(kv)
        
        # Populate both sides with identical content
        self._populate_content(root.ids.kivy_content)
        self._populate_content(root.ids.flutter_content)
        
        # Add effect parameter info
        self._add_effect_info(root.ids.kivy_scroll, root.ids.flutter_scroll)
        
        return root
    
    def _populate_content(self, container):
        '''Add sample content to a container.'''
        # Header
        header = ComparisonLabel(
            '[b][size=20]Scroll Effect Test[/size][/b]',
        )
        header.markup = True
        container.add_widget(header)
        
        # Instructions
        instructions = ComparisonLabel(
            '[b]Instructions:[/b]\n'
            '1. Scroll to the top or bottom edge\n'
            '2. Fling past the edge with some speed\n'
            '3. Watch how it bounces back\n'
            '4. Compare left vs right behavior',
        )
        instructions.markup = True
        container.add_widget(instructions)
        
        # Add numbered items to make scrolling obvious
        for i in range(1, 31):
            label = ComparisonLabel(f'Item {i}')
            
            # Add some background color for visibility
            from kivy.graphics import Color, Rectangle
            with label.canvas.before:
                Color(0.15, 0.15, 0.15, 1)
                label.rect = Rectangle(pos=label.pos, size=label.size)
            label.bind(pos=self._update_rect, size=self._update_rect)
            
            container.add_widget(label)
        
        # Footer
        footer = ComparisonLabel(
            '[b][size=18]End of Content[/size][/b]\n'
            'Try scrolling back to the top!',
        )
        footer.markup = True
        container.add_widget(footer)
    
    def _update_rect(self, instance, value):
        '''Update background rectangle position/size.'''
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def _add_effect_info(self, kivy_scroll, flutter_scroll):
        '''Print effect information to console.'''
        print("\n" + "="*60)
        print("SCROLL EFFECT COMPARISON")
        print("="*60)
        
        print("\nLEFT SIDE - Kivy DampedScrollEffect:")
        print(f"  - Type: {type(kivy_scroll.effect_y).__name__}")
        if hasattr(kivy_scroll.effect_y, 'spring_constant'):
            print(f"  - spring_constant: {kivy_scroll.effect_y.spring_constant}")
            print(f"  - edge_damping: {kivy_scroll.effect_y.edge_damping}")
            print(f"  - Status: UNDERDAMPED (may oscillate)")
        
        print("\nRIGHT SIDE - Flutter-inspired Effect:")
        print(f"  - Type: {type(flutter_scroll.effect_y).__name__}")
        if hasattr(flutter_scroll.effect_y, 'spring_stiffness'):
            print(f"  - spring_stiffness: {flutter_scroll.effect_y.spring_stiffness}")
            print(f"  - spring_mass: {flutter_scroll.effect_y.spring_mass}")
            print(f"  - rubber_band_coeff: {flutter_scroll.effect_y.rubber_band_coeff}")
            
            # Calculate critical damping
            from math import sqrt
            k = flutter_scroll.effect_y.spring_stiffness
            m = flutter_scroll.effect_y.spring_mass
            critical_damping = 2.0 * sqrt(k * m)
            print(f"  - critical_damping: {critical_damping:.2f}")
            print(f"  - Status: CRITICALLY DAMPED (no oscillation)")
        
        print("\nTEST INSTRUCTIONS:")
        print("  1. Scroll each view to top/bottom")
        print("  2. Fling past the edge with velocity")
        print("  3. Observe bounce-back behavior")
        print("  4. Left may oscillate, right should be smooth")
        print("="*60 + "\n")


if __name__ == '__main__':
    EffectComparisonDemo().run()

