"""
find_scroll_stop.py

A diagnostic tool to observe ScrollView behavior with different scroll effects.
Displays scroll position (scroll_x, scroll_y) and velocity values in real-time.

Used to explore options for implementing updated on_scroll events
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from updated_sv import ScrollView


class ScrollObserverApp(App):
    def build(self):
        # Track if scroll is in motion
        self.was_scrolling = False
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Control panel at the top
        control_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        # Spinner for scroll effect selection
        effect_label = Label(text='Scroll Effect:', size_hint_x=0.3)
        self.effect_spinner = Spinner(
            text='DampedScrollEffect',
            values=('DampedScrollEffect', 'ScrollEffect', 'OpacityScrollEffect'),
            size_hint_x=0.7
        )
        self.effect_spinner.bind(text=self.on_effect_change)
        
        control_panel.add_widget(effect_label)
        control_panel.add_widget(self.effect_spinner)
        
        # Info display panel
        info_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=150, spacing=5)
        
        # Left column - scroll position
        left_info = BoxLayout(orientation='vertical')
        left_info.add_widget(Label(text='[b]Scroll Position[/b]', markup=True, size_hint_y=0.25))
        self.scroll_x_label = Label(text='scroll_x: 0.0', size_hint_y=0.25)
        self.scroll_y_label = Label(text='scroll_y: 1.0', size_hint_y=0.25)
        self.motion_status_label = Label(text='[b]Status:[/b] Stopped', markup=True, size_hint_y=0.25)
        left_info.add_widget(self.scroll_x_label)
        left_info.add_widget(self.scroll_y_label)
        left_info.add_widget(self.motion_status_label)
        
        # Right column - velocity
        right_info = BoxLayout(orientation='vertical')
        right_info.add_widget(Label(text='[b]Velocity[/b]', markup=True, size_hint_y=0.25))
        self.vel_x_label = Label(text='vel_x: 0.0', size_hint_y=0.25)
        self.vel_y_label = Label(text='vel_y: 0.0', size_hint_y=0.25)
        right_info.add_widget(self.vel_x_label)
        right_info.add_widget(self.vel_y_label)
        # Empty space for alignment
        right_info.add_widget(Label(text='', size_hint_y=0.25))
        
        info_panel.add_widget(left_info)
        info_panel.add_widget(right_info)
        
        # ScrollView with content
        self.scrollview = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            bar_width=10,
            scroll_type=['bars', 'content']
        )
        
        # Create scrollable content - a grid of buttons
        content = GridLayout(cols=3, spacing=10, size_hint=(None, None), padding=10)
        content.bind(minimum_height=content.setter('height'))
        content.bind(minimum_width=content.setter('width'))
        
        # Add many buttons to make it scrollable
        for i in range(50):
            btn = Button(
                text=f'Button {i+1}',
                size_hint=(None, None),
                size=(150, 100)
            )
            content.add_widget(btn)
        
        self.scrollview.add_widget(content)
        
        # Bind scroll properties to update labels
        self.scrollview.bind(scroll_x=self.update_scroll_values)
        self.scrollview.bind(scroll_y=self.update_scroll_values)
        
        # Bind to effect velocity changes (more efficient than polling)
        self.bind_velocity_updates()
        
        # Bind to scroll events for testing
        self.scrollview.bind(on_scroll_start=self.on_scroll_start_event)
        
        # Assemble the UI
        main_layout.add_widget(control_panel)
        main_layout.add_widget(info_panel)
        main_layout.add_widget(self.scrollview)
        
        return main_layout
    
    def on_effect_change(self, spinner, effect_name):
        # Change the scroll effect based on spinner selection
        self.scrollview.effect_cls = effect_name
        # Rebind to new effect's velocity property
        self.bind_velocity_updates()
    
    def bind_velocity_updates(self):
        # Bind to velocity property of both effects
        # This is more efficient than polling - only triggers when velocity changes
        self.scrollview.effect_x.bind(velocity=self.update_velocity_values)
        self.scrollview.effect_y.bind(velocity=self.update_velocity_values)
    
    def update_scroll_values(self, instance, value):
        # Update scroll position labels
        self.scroll_x_label.text = f'scroll_x: {self.scrollview.scroll_x:.4f}'
        self.scroll_y_label.text = f'scroll_y: {self.scrollview.scroll_y:.4f}'
    
    def on_scroll_start_event(self, instance, touch):
        """Handle on_scroll_start event for testing"""
        print(f'[EVENT] on_scroll_start fired - scroll gesture detected')
        print(f'[EVENT] Touch position: {touch.pos}')
        print(f'[EVENT] Scroll position: x={self.scrollview.scroll_x:.4f}, y={self.scrollview.scroll_y:.4f}')
        print('-' * 40)
    
    def update_velocity_values(self, instance, value):
        # Update velocity labels from the scroll effects (triggered by velocity property change)
        vel_x = 0.0
        vel_y = 0.0
        
        if hasattr(self.scrollview, 'effect_x') and self.scrollview.effect_x:
            vel_x = self.scrollview.effect_x.velocity
        
        if hasattr(self.scrollview, 'effect_y') and self.scrollview.effect_y:
            vel_y = self.scrollview.effect_y.velocity
        
        self.vel_x_label.text = f'vel_x: {vel_x:.2f}'
        self.vel_y_label.text = f'vel_y: {vel_y:.2f}'
        
        # Threshold for considering velocity as zero (to handle floating point imprecision)
        velocity_threshold = 0.1
        
        # Check if scroll is in motion
        is_scrolling = abs(vel_x) > velocity_threshold or abs(vel_y) > velocity_threshold
        
        if is_scrolling:
            # Scroll is in motion
            self.was_scrolling = True
            self.motion_status_label.text = '[b]Status:[/b] [color=00ff00]Scrolling[/color]'
            # Print to console when velocity is non-zero (for debugging)
            # print(f'Scrolling - X: {self.scrollview.scroll_x:.4f}, Y: {self.scrollview.scroll_y:.4f}, '
            #       f'VelX: {vel_x:.2f}, VelY: {vel_y:.2f}')
        elif self.was_scrolling:
            # Velocity just reached zero - motion has stopped!
            self.was_scrolling = False
            self.motion_status_label.text = '[b]Status:[/b] [color=ff0000]Stopped[/color]'
            print(f'>>> SCROLL MOTION STOPPED <<< Final Position - X: {self.scrollview.scroll_x:.4f}, Y: {self.scrollview.scroll_y:.4f}')
            print('-' * 60)


if __name__ == '__main__':
    ScrollObserverApp().run()

