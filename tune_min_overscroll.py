"""
Visual comparison tool for DampedScrollEffect parameters.

Left panel: XY ScrollView with default values
Right panel: XY ScrollView with adjustable parameters (controlled by sliders)

Parameters:
- min_overscroll: Overscroll values below this snap to zero (prevents oscillation)
- edge_damping: Extra damping force in overscroll region (affects bounce speed)
- spring_constant: Spring force strength (affects bounce-back speed)

This allows side-by-side comparison of how different parameters
affect the elastic bounce and settling behavior.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.effects.dampedscroll import DampedScrollEffect
from scrollview import ScrollView


class FixedDampedScrollEffect(DampedScrollEffect):
    """Fixed DampedScrollEffect that only snaps overscroll to 0 during automatic settling.
    
    The original DampedScrollEffect has a bug where min_overscroll creates a dead zone
    during manual dragging. This fix ensures the snap-to-zero logic only applies when
    the effect is settling automatically (not during manual touch/drag).
    """
    
    def update_velocity(self, dt):
        if abs(self.velocity) <= self.min_velocity and self.overscroll == 0:
            self.velocity = 0
            if self.round_value:
                self.value = round(self.value)
            return

        total_force = self.velocity * self.friction * dt / self.std_dt
        
        # FIX 1: Only snap overscroll to 0 during automatic settling, not manual dragging
        # FIX 2: When snapping overscroll to 0, also snap value to exact boundary
        if abs(self.overscroll) > self.min_overscroll:
            total_force += self.velocity * self.edge_damping
            total_force += self.overscroll * self.spring_constant
        elif not self.is_manual:
            # Snap overscroll to 0 when below threshold during automatic settling
            if self.overscroll != 0:
                # Also snap value to exact boundary to prevent offset settling
                # Note: Need to normalize min/max since they can be reversed (Y-axis)
                scroll_min = self.min
                scroll_max = self.max
                if scroll_min > scroll_max:
                    scroll_min, scroll_max = scroll_max, scroll_min
                
                if self.overscroll < 0:
                    # Below minimum boundary
                    self.value = scroll_min
                else:
                    # Above maximum boundary
                    self.value = scroll_max
                self.overscroll = 0
                self.velocity = 0
                return

        stop_overscroll = ''
        if not self.is_manual:
            if self.overscroll > 0 and self.velocity < 0:
                stop_overscroll = 'max'
            elif self.overscroll < 0 and self.velocity > 0:
                stop_overscroll = 'min'

        self.velocity = self.velocity - total_force
        if not self.is_manual:
            self.apply_distance(self.velocity * dt)
            if stop_overscroll == 'min' and self.value > self.min:
                self.value = self.min
                self.velocity = 0
                return
            if stop_overscroll == 'max' and self.value < self.max:
                self.value = self.max
                self.velocity = 0
                return
        self.trigger_velocity_update()


class TuneMinOverscrollApp(App):
    def build(self):
        # Main horizontal layout
        root = BoxLayout(orientation='horizontal', spacing=5, padding=5)
        
        # Left panel - Default values (original DampedScrollEffect)
        left_container = BoxLayout(orientation='vertical', size_hint_x=0.4)
        left_label = Label(
            text='Original DampedScrollEffect\nmin_overscroll=0.5  edge_damping=0.25  spring=2.0',
            size_hint_y=None,
            height=50,
            font_size='14sp',
            bold=True
        )
        self.left_sv = self._create_scrollview(
            min_overscroll=0.5,
            edge_damping=0.25,
            spring_constant=2.0,
            use_fixed=False
        )
        left_container.add_widget(left_label)
        left_container.add_widget(self.left_sv)
        
        # Right panel - Adjustable parameters (fixed version)
        right_container = BoxLayout(orientation='vertical', size_hint_x=0.4)
        self.right_label = Label(
            text='FixedDampedScrollEffect (Adjustable)\nmin_overscroll=0.5  edge_damping=0.25  spring=2.0',
            size_hint_y=None,
            height=50,
            font_size='14sp',
            bold=True
        )
        self.right_sv = self._create_scrollview(
            min_overscroll=0.5,
            edge_damping=0.25,
            spring_constant=2.0,
            use_fixed=True
        )
        right_container.add_widget(self.right_label)
        right_container.add_widget(self.right_sv)
        
        # Far right - Slider controls
        controls_container = BoxLayout(orientation='vertical', size_hint_x=0.2, spacing=5)
        
        # min_overscroll slider
        controls_container.add_widget(self._create_parameter_slider(
            param_name='min_overscroll',
            min_val=0,
            max_val=5,
            default_val=0.5,
            step=0.05,
            callback=self.on_min_overscroll_change
        ))
        
        # edge_damping slider
        controls_container.add_widget(self._create_parameter_slider(
            param_name='edge_damping',
            min_val=0,
            max_val=1.5,
            default_val=0.25,
            step=0.05,
            callback=self.on_edge_damping_change
        ))
        
        # spring_constant slider
        controls_container.add_widget(self._create_parameter_slider(
            param_name='spring_constant',
            min_val=0,
            max_val=3.0,
            default_val=2.0,
            step=0.1,
            callback=self.on_spring_constant_change
        ))
        
        # Add all panels to root
        root.add_widget(left_container)
        root.add_widget(right_container)
        root.add_widget(controls_container)
        
        return root
    
    def _create_parameter_slider(self, param_name, min_val, max_val, default_val, step, callback):
        """Create a labeled slider control for a parameter."""
        container = BoxLayout(orientation='vertical', spacing=2)
        
        # Parameter name label
        name_label = Label(
            text=param_name,
            size_hint_y=None,
            height=25,
            font_size='13sp',
            bold=True
        )
        
        # Value display
        value_label = Label(
            text=f'{default_val:.2f}',
            size_hint_y=None,
            height=30,
            font_size='18sp',
            bold=True
        )
        
        # Slider
        slider = Slider(
            min=min_val,
            max=max_val,
            value=default_val,
            orientation='vertical',
            step=step
        )
        
        # Store references for callbacks
        setattr(self, f'{param_name}_label', value_label)
        setattr(self, f'{param_name}_slider', slider)
        
        slider.bind(value=lambda instance, value: callback(value))
        
        # Min/Max labels
        max_label = Label(text=f'{max_val}', size_hint_y=None, height=20, font_size='11sp')
        min_label = Label(text=f'{min_val}', size_hint_y=None, height=20, font_size='11sp')
        
        container.add_widget(name_label)
        container.add_widget(value_label)
        container.add_widget(max_label)
        container.add_widget(slider)
        container.add_widget(min_label)
        
        return container
    
    def _create_scrollview(self, min_overscroll, edge_damping, spring_constant, use_fixed=True):
        """Create an XY ScrollView with a grid of colored buttons."""
        # Create ScrollView with custom effect
        sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=10
        )
        
        # Set effect class with custom parameters
        if use_fixed:
            # Use fixed version that prevents dead zone during manual drag
            class CustomEffect(FixedDampedScrollEffect):
                pass
        else:
            # Use original DampedScrollEffect for comparison
            class CustomEffect(DampedScrollEffect):
                pass
        
        CustomEffect.min_overscroll = min_overscroll
        CustomEffect.edge_damping = edge_damping
        CustomEffect.spring_constant = spring_constant
        sv.effect_cls = CustomEffect
        
        # Create grid layout with colored buttons
        grid = GridLayout(
            cols=8,
            spacing=5,
            size_hint=(None, None),
            padding=10
        )
        
        # Make grid larger than ScrollView
        grid.bind(minimum_height=grid.setter('height'))
        grid.bind(minimum_width=grid.setter('width'))
        
        # Define colors for buttons
        colors = [
            (1, 0.3, 0.3, 1),    # Red
            (0.3, 1, 0.3, 1),    # Green
            (0.3, 0.3, 1, 1),    # Blue
            (1, 1, 0.3, 1),      # Yellow
            (1, 0.3, 1, 1),      # Magenta
            (0.3, 1, 1, 1),      # Cyan
            (1, 0.6, 0.3, 1),    # Orange
            (0.6, 0.3, 1, 1),    # Purple
        ]
        
        # Create 20 rows x 8 cols = 160 buttons
        for row in range(20):
            for col in range(8):
                color = colors[col % len(colors)]
                btn = Button(
                    text=f'{row},{col}',
                    size_hint=(None, None),
                    size=(100, 60),
                    background_color=color,
                    background_normal=''
                )
                grid.add_widget(btn)
        
        sv.add_widget(grid)
        return sv
    
    def on_min_overscroll_change(self, value):
        """Update right ScrollView's min_overscroll when slider changes."""
        # Update the value label
        self.min_overscroll_label.text = f'{value:.2f}'
        
        # Update the effect's min_overscroll value in real-time
        if self.right_sv.effect_x:
            self.right_sv.effect_x.min_overscroll = value
        if self.right_sv.effect_y:
            self.right_sv.effect_y.min_overscroll = value
    
    def on_edge_damping_change(self, value):
        """Update right ScrollView's edge_damping when slider changes."""
        # Update the value label
        self.edge_damping_label.text = f'{value:.2f}'
        
        # Update the effect's edge_damping value in real-time
        if self.right_sv.effect_x:
            self.right_sv.effect_x.edge_damping = value
        if self.right_sv.effect_y:
            self.right_sv.effect_y.edge_damping = value
    
    def on_spring_constant_change(self, value):
        """Update right ScrollView's spring_constant when slider changes."""
        # Update the value label
        self.spring_constant_label.text = f'{value:.2f}'
        
        # Update the effect's spring_constant value in real-time
        if self.right_sv.effect_x:
            self.right_sv.effect_x.spring_constant = value
        if self.right_sv.effect_y:
            self.right_sv.effect_y.spring_constant = value


if __name__ == '__main__':
    TuneMinOverscrollApp().run()

