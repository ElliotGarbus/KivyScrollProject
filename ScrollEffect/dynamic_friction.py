"""
Dynamic Friction Effect 
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from flutter_scroll_effect import FlutterScrollEffect

# Register the effect
Factory.register('FlutterScrollEffect', cls=FlutterScrollEffect)

# KV language for the UI
kv = '''
BoxLayout:
    orientation: 'horizontal'
    spacing: dp(10)
    padding: dp(10)
    
    # Left side - Parameter controls
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.4
        spacing: dp(8)
        
        Label:
            size_hint_y: None
            height: dp(40)
            text: 'FLUTTER EFFECT TUNING'
            font_size: '16sp'
            bold: True
            color: 1, 1, 1, 1
        
        # Rubber Band Coefficient
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(80)
            
            Label:
                size_hint_y: None
                height: dp(25)
                text: 'Rubber Band Coefficient: {:.2f}'.format(rubber_band_slider.value)
                font_size: '12sp'
                halign: 'left'
                text_size: self.size
            
            Slider:
                id: rubber_band_slider
                min: 0.1
                max: 1.5
                value: 0.55
                step: 0.05
                size_hint_y: None
                height: dp(30)
                on_value: app.update_rubber_band(self.value)
            
            Label:
                size_hint_y: None
                height: dp(20)
                text: 'Lower = Stiffer | Higher = More elastic'
                font_size: '9sp'
                color: 0.7, 0.7, 0.7, 1
        
        # Spring Stiffness
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(80)
            
            Label:
                size_hint_y: None
                height: dp(25)
                text: 'Spring Stiffness: {:.1f}'.format(spring_stiffness_slider.value)
                font_size: '12sp'
                halign: 'left'
                text_size: self.size
            
            Slider:
                id: spring_stiffness_slider
                min: 20
                max: 300
                value: 100
                step: 10
                size_hint_y: None
                height: dp(30)
                on_value: app.update_spring_stiffness(self.value)
            
            Label:
                size_hint_y: None
                height: dp(20)
                text: 'Lower = Slower bounce | Higher = Faster bounce'
                font_size: '9sp'
                color: 0.7, 0.7, 0.7, 1
        
        # Spring Mass
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(80)
            
            Label:
                size_hint_y: None
                height: dp(25)
                text: 'Spring Mass: {:.2f}'.format(spring_mass_slider.value)
                font_size: '12sp'
                halign: 'left'
                text_size: self.size
            
            Slider:
                id: spring_mass_slider
                min: 0.1
                max: 3.0
                value: 1.0
                step: 0.1
                size_hint_y: None
                height: dp(30)
                on_value: app.update_spring_mass(self.value)
            
            Label:
                size_hint_y: None
                height: dp(20)
                text: 'Affects momentum and bounce speed'
                font_size: '9sp'
                color: 0.7, 0.7, 0.7, 1
        
        # Min Overscroll
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(80)
            
            Label:
                size_hint_y: None
                height: dp(25)
                text: 'Min Overscroll: {:.2f}'.format(min_overscroll_slider.value)
                font_size: '12sp'
                halign: 'left'
                text_size: self.size
            
            Slider:
                id: min_overscroll_slider
                min: 0.0
                max: 5.0
                value: 0.5
                step: 0.1
                size_hint_y: None
                height: dp(30)
                on_value: app.update_min_overscroll(self.value)
            
            Label:
                size_hint_y: None
                height: dp(20)
                text: 'Threshold for activating overscroll'
                font_size: '9sp'
                color: 0.7, 0.7, 0.7, 1
        
        # Friction (inherited from KineticEffect)
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(80)
            
            Label:
                size_hint_y: None
                height: dp(25)
                text: 'Friction: {:.3f}'.format(friction_slider.value)
                font_size: '12sp'
                halign: 'left'
                text_size: self.size
            
            Slider:
                id: friction_slider
                min: 0.01
                max: 0.2
                value: 0.05
                step: 0.01
                size_hint_y: None
                height: dp(30)
                on_value: app.update_friction(self.value)
            
            Label:
                size_hint_y: None
                height: dp(20)
                text: 'Deceleration rate (momentum scrolling)'
                font_size: '9sp'
                color: 0.7, 0.7, 0.7, 1
        
        # Min Velocity (inherited from KineticEffect)
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(80)
            
            Label:
                size_hint_y: None
                height: dp(25)
                text: 'Min Velocity: {:.2f}'.format(min_velocity_slider.value)
                font_size: '12sp'
                halign: 'left'
                text_size: self.size
            
            Slider:
                id: min_velocity_slider
                min: 0.1
                max: 20.0
                value: 0.5
                step: 0.5
                size_hint_y: None
                height: dp(30)
                on_value: app.update_min_velocity(self.value)
            
            Label:
                size_hint_y: None
                height: dp(20)
                text: 'Higher = stops earlier (more abrupt), Lower = slow creep'
                font_size: '9sp'
                color: 0.7, 0.7, 0.7, 1
        
        # Calculated critical damping display
        # Label:
        #     size_hint_y: None
        #     height: dp(40)
        #     text: 'Critical Damping: {:.2f}'.format(app.get_critical_damping())
        #     font_size: '11sp'
        #     color: 0.3, 1.0, 0.3, 1
        
        # Reset button
        Button:
            size_hint_y: None
            height: dp(45)
            text: 'RESET TO DEFAULTS'
            font_size: '12sp'
            bold: True
            on_press: app.reset_defaults()
        
        # Spacer
        Widget:
    
    # Right side - ScrollView with test content
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.6
        
        Label:
            size_hint_y: None
            height: dp(40)
            text: 'TEST SCROLL AREA'
            font_size: '16sp'
            bold: True
            color: 0.3, 0.8, 1.0, 1
        
        DynamicFrictionScrollView:
            id: test_scroll
            do_scroll_x: False
            do_scroll_y: True
            scroll_type: ['bars', 'content']
            bar_width: dp(10)
            bar_color: 0.3, 0.8, 1.0, 0.8
            effect_cls: 'FlutterScrollEffect'
            
            BoxLayout:
                id: scroll_content
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                spacing: dp(5)
'''


class DynamicFrictionScrollView(ScrollView):
    def on_kv_post(self, base_widget):
        self.effect_y.bind(velocity=self.update_friction)

    def update_friction(self, instance, value):
        """
        Dynamic friction that provides smooth deceleration.
        
        Strategy: Use lower friction at low speeds for smooth stops,
        higher friction at high speeds for controlled movement.
        """
        abs_velocity = abs(value)
        print(f"abs_velocity: {abs_velocity}")
        base_friction = 0.01
        if abs_velocity > 50:
            velocity_component = 0.03 + (abs_velocity / 10000.0)
        elif abs_velocity > 5:
            velocity_component = 0.015 + (abs_velocity / 5000.0)
        else:
            velocity_component = 0.005
        final_friction = base_friction + velocity_component
        print(f"final_friction: {final_friction}")
        self.effect_y.friction = min(final_friction, 0.15)  # Cap at 0.15


class ColoredLabel(Label):
    '''A label with a colored background.'''
    def __init__(self, text, bg_color=(0.2, 0.25, 0.3, 1), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = '13sp'
        self.padding = (10, 10)
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class FlutterTuningDemo(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effect = None  # Initialize early to avoid AttributeError
    
    def build(self):
        Window.size = (800, 700)
        self.root = Builder.load_string(kv)
        
        # Get reference to the ScrollView's effect
        self.scroll_view = self.root.ids.test_scroll
        
        # Populate content
        self._populate_content()
        
        # Store the effect after it's created
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._store_effect(), 0.1)
        
        return self.root
    
    def _store_effect(self):
        '''Store reference to the Y effect for updates.'''
        self.effect = self.scroll_view.effect_y
        print(f"\nEffect stored: {type(self.effect).__name__}")
        print(f"Initial parameters:")
        print(f"  - rubber_band_coeff: {self.effect.rubber_band_coeff}")
        print(f"  - spring_stiffness: {self.effect.spring_stiffness}")
        print(f"  - spring_mass: {self.effect.spring_mass}")
        print(f"  - min_overscroll: {self.effect.min_overscroll}")
        print(f"  - friction: {self.effect.friction}")
        print(f"  - min_velocity: {self.effect.min_velocity}")
        print(f"  - critical_damping: {self.get_critical_damping():.2f}\n")
    
    def _populate_content(self):
        '''Populate the ScrollView with test content.'''
        container = self.root.ids.scroll_content
        
        colors = [
            (0.2, 0.3, 0.5, 1),
            (0.3, 0.2, 0.5, 1),
            (0.2, 0.5, 0.3, 1),
            (0.5, 0.3, 0.2, 1),
            (0.5, 0.5, 0.2, 1),
        ]
        
        # Header
        header = ColoredLabel(
            '[b]SCROLL TEST CONTENT[/b]\n'
            'Adjust parameters on the left and scroll to feel the changes!\n'
            'Try flinging past the top or bottom edge.',
            bg_color=(0.15, 0.25, 0.35, 1)
        )
        header.markup = True
        header.size_hint_y = None
        header.height = 90
        container.add_widget(header)
        
        # Add 40 items
        for i in range(1, 41):
            label = ColoredLabel(
                f'[b]Item {i}[/b] - Scroll content. Fling past edges to test the rubber band effect!',
                bg_color=colors[i % len(colors)]
            )
            label.markup = True
            label.size_hint_y = None
            label.height = 55
            container.add_widget(label)
        
        # Footer
        footer = ColoredLabel(
            '[b]END OF CONTENT[/b]\n'
            'Try different parameter combinations!',
            bg_color=(0.15, 0.25, 0.35, 1)
        )
        footer.markup = True
        footer.size_hint_y = None
        footer.height = 70
        container.add_widget(footer)
    
    def update_rubber_band(self, value):
        '''Update rubber band coefficient.'''
        if self.effect:
            self.effect.rubber_band_coeff = value
            print(f"rubber_band_coeff updated: {value:.2f}")
    
    def update_spring_stiffness(self, value):
        '''Update spring stiffness.'''
        if self.effect:
            self.effect.spring_stiffness = value
            print(f"spring_stiffness updated: {value:.1f} | critical_damping: {self.get_critical_damping():.2f}")
    
    def update_spring_mass(self, value):
        '''Update spring mass.'''
        if self.effect:
            self.effect.spring_mass = value
            print(f"spring_mass updated: {value:.2f} | critical_damping: {self.get_critical_damping():.2f}")
    
    def update_min_overscroll(self, value):
        '''Update min overscroll threshold.'''
        if self.effect:
            self.effect.min_overscroll = value
            print(f"min_overscroll updated: {value:.2f}")
    
    def update_friction(self, value):
        '''Update friction.'''
        if self.effect:
            self.effect.friction = value
            print(f"friction updated: {value:.3f}")
    
    def update_min_velocity(self, value):
        '''Update min velocity.'''
        if self.effect:
            self.effect.min_velocity = value
            print(f"min_velocity updated: {value:.2f}")
    
    def get_critical_damping(self):
        '''Calculate and return critical damping value.'''
        if self.effect:
            from math import sqrt
            return 2.0 * sqrt(self.effect.spring_stiffness * self.effect.spring_mass)
        return 0.0
    
    def reset_defaults(self):
        '''Reset all parameters to defaults.'''
        print("\nResetting to defaults...")
        
        # Reset effect parameters
        if self.effect:
            self.effect.rubber_band_coeff = 0.55
            self.effect.spring_stiffness = 100.0
            self.effect.spring_mass = 1.0
            self.effect.min_overscroll = 0.5
            self.effect.friction = 0.05
            self.effect.min_velocity = 0.5
        
        # Reset sliders
        self.root.ids.rubber_band_slider.value = 0.55
        self.root.ids.spring_stiffness_slider.value = 100.0
        self.root.ids.spring_mass_slider.value = 1.0
        self.root.ids.min_overscroll_slider.value = 0.5
        self.root.ids.friction_slider.value = 0.05
        self.root.ids.min_velocity_slider.value = 0.5
        
        print("Reset complete!\n")


if __name__ == '__main__':
    FlutterTuningDemo().run()

