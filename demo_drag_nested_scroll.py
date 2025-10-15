"""
demo_drag_nested_scroll.py

Demo showing dragging buttons OUT of nested orthogonal ScrollViews to a landing zone.
Tests that DragBehavior works correctly with buttons inside nested ScrollViews.

Features:
- Nested orthogonal ScrollViews (Vertical outer + Horizontal inner rows)
- Drag buttons from any row to the landing zone
- Buttons that hit the landing zone are removed from their row
- Buttons that miss return to their original position
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.behaviors import DragBehavior
from kivy.properties import BooleanProperty, ListProperty
from kivy.animation import Animation
from kivy.clock import Clock
from updated_sv_no_manager import ScrollView


class DraggableButton(DragBehavior, Button):
    """Button that can be dragged from nested ScrollViews to a landing zone."""
    dragging = BooleanProperty(False)
    original_pos = ListProperty([0, 0])
    original_parent = None
    float_parent = None  # Will hold reference to FloatLayout for reparenting
    original_index = 0
    reparented = False  # Track if we've already reparented
    touch_start_pos = None  # Track where touch started
    active_touch = None  # Track the touch that pressed this button
    was_pressed = False  # Track if button was pressed (on_press fired)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set drag properties
        self.drag_timeout = 200
        self.drag_distance = 10
        # Bind to update drag_rectangle when position/size changes
        self.bind(pos=self.update_drag_rectangle, size=self.update_drag_rectangle)
        # Bind to on_press to detect button clicks
        self.bind(on_press=self.handle_press)
    
    def update_drag_rectangle(self, *args):
        """Update drag_rectangle to match button's current position and size."""
        self.drag_rectangle = [self.x, self.y, self.width, self.height]
    
    def handle_press(self, instance):
        """Called when button is pressed (clicked without dragging)."""
        self.was_pressed = True
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Store original state for potential drag
            self.original_pos = self.to_window(*self.pos)
            self.original_parent = self.parent
            self.original_index = self.parent.children.index(self)
            self.reparented = False
            self.dragging = False
            self.was_pressed = False
            self.touch_start_pos = touch.pos[:]
            self.active_touch = touch
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        # Check if this is our active touch and has moved beyond drag_distance
        if self.active_touch is touch and self.touch_start_pos and not self.reparented:
            dx = touch.pos[0] - self.touch_start_pos[0]
            dy = touch.pos[1] - self.touch_start_pos[1]
            distance = (dx**2 + dy**2)**0.5
            
            # Don't reparent if button was pressed (not a drag gesture)
            if self.was_pressed:
                return super().on_touch_move(touch)
            
            # Reparent when drag threshold is exceeded
            if distance >= self.drag_distance and self.float_parent and self.parent != self.float_parent:
                # Store original size and position
                original_size = self.size[:]
                window_pos = self.to_window(*self.pos)
                
                # Reparent to FloatLayout so button appears on top during drag
                self.parent.remove_widget(self)
                self.size_hint = (None, None)
                self.size = original_size
                self.float_parent.add_widget(self)
                self.pos = self.float_parent.to_widget(*window_pos)
                
                self.reparented = True
                self.dragging = True
                self.opacity = 0.6
        
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        # If button was pressed and got reparented, restore it immediately
        if self.was_pressed and self.reparented and self.parent != self.original_parent:
            self.parent.remove_widget(self)
            self.original_parent.add_widget(self, index=self.original_index)
            self.pos = self.original_parent.to_widget(*self.original_pos)
            self.reparented = False
            self.dragging = False
            self.opacity = 1
        
        # Cleanup
        if touch is self.active_touch:
            self.active_touch = None
        if self.dragging:
            self.opacity = 1
            self.dragging = False
        return super().on_touch_up(touch)


class LandingZone(Widget):
    """Visual landing zone that highlights when a button is dropped on it."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_color = [0.3, 0.3, 0.3, 1]  # Gray
        self.hover_color = [0.5, 0.5, 0.1, 1]    # Yellow
        self.success_color = [0.1, 0.6, 0.1, 1]  # Green
        
        with self.canvas.before:
            self.bg_color = Color(*self.default_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Add label
        self.label = Label(
            text='Drop Zone\n(Remove from list)',
            bold=True,
            color=[1, 1, 1, 1],
            halign='center',
            valign='middle',
            size_hint=(1, 1)
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)
    
    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        # Also update label position to match
        self.label.pos = self.pos
        self.label.size = self.size
    
    def set_hover(self, is_hovering):
        """Change color when button is hovering over landing zone."""
        if is_hovering:
            self.bg_color.rgba = self.hover_color
        else:
            self.bg_color.rgba = self.default_color
    
    def set_success(self):
        """Change to success color when button is dropped successfully."""
        self.bg_color.rgba = self.success_color
    
    def reset(self):
        """Reset to default color."""
        self.bg_color.rgba = self.default_color


class DragNestedScrollDemo(App):
    def build(self):
        # Root layout
        root = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Title
        title = Label(
            text='[b]Drag From Nested ScrollView Demo[/b]\n'
                 'Vertical outer + Horizontal inner rows | Drag buttons to drop zone',
            markup=True,
            size_hint=(1, None),
            height=dp(60)
        )
        root.add_widget(title)
        
        # Main content area - FloatLayout for absolute positioning
        main_area = FloatLayout(size_hint=(1, 1))
        
        # Background BoxLayout for structured content
        content_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            padding=dp(10),
            size_hint=(1, 1)
        )
        
        # Left side: Landing zone (30%) - First in widget tree so it's below dragged buttons
        landing_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.3
        )
        
        landing_label = Label(
            text='Drop Here',
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        landing_container.add_widget(landing_label)
        
        self.landing_zone = LandingZone(size_hint=(1, 1))
        landing_container.add_widget(self.landing_zone)
        
        content_layout.add_widget(landing_container)
        
        # Right side: Nested ScrollViews with draggable buttons (70%)
        nested_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.7
        )
        
        nested_label = Label(
            text='Nested ScrollViews: Scroll vertically through rows, horizontally within rows',
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        nested_container.add_widget(nested_label)
        
        # Outer ScrollView (Vertical)
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        # Outer content container (vertical layout with multiple horizontal ScrollViews)
        outer_content = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=None
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Create 6 horizontal ScrollViews (rows) with draggable buttons
        for row_num in range(6):
            # Row container
            row_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(120),
                spacing=dp(5)
            )
            
            # Row label
            row_label = Label(
                text=f'Row {row_num + 1} - Scroll horizontally -',
                size_hint_y=None,
                height=dp(25),
                bold=True
            )
            row_container.add_widget(row_label)
            
            # Inner ScrollView (Horizontal)
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint_y=None,
                height=dp(95),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8],
                smooth_scroll_end=10
            )
            
            # Horizontal content for inner ScrollView
            inner_content = BoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_x=None,
                padding=dp(5)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            
            # Add 15 draggable buttons to each row
            for btn_num in range(15):
                btn = DraggableButton(
                    text=f'R{row_num+1}-{btn_num+1}',
                    size_hint_x=None,
                    width=dp(80),
                    height=dp(70),
                    background_color=[0.2 + (row_num * 0.1) % 0.6, 0.3, 0.7, 1]
                )
                # Set reference to FloatLayout for reparenting during drag
                btn.float_parent = main_area
                # Bind to handle drag completion
                btn.bind(on_touch_up=self.on_button_drag_complete)
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            row_container.add_widget(inner_sv)
            outer_content.add_widget(row_container)
        
        outer_sv.add_widget(outer_content)
        nested_container.add_widget(outer_sv)
        
        content_layout.add_widget(nested_container)
        
        # Add content layout to main area
        main_area.add_widget(content_layout)
        
        # Add main area to root
        root.add_widget(main_area)
        
        return root
    
    def on_button_drag_complete(self, instance, touch):
        """Called when a button's drag is complete (on_touch_up)."""
        # Only process if this button was being dragged
        if not hasattr(instance, 'dragging') or not instance.dragging:
            return
        
        print(f"[DRAG] Button '{instance.text}' drag completed")
        
        # Use touch position directly to check collision with landing zone
        # Transform touch position to landing zone's coordinate space
        touch.push()
        touch.apply_transform_2d(self.landing_zone.to_widget)
        collision = self.landing_zone.collide_point(*touch.pos)
        touch.pop()
        
        if collision:
            # Success! Button dropped in landing zone
            print(f"[SUCCESS] Button '{instance.text}' dropped in landing zone - REMOVING")
            self.landing_zone.set_success()
            
            # Remove the button from its row
            if instance.parent:
                instance.parent.remove_widget(instance)
            
            # Reset landing zone color after a delay
            Clock.schedule_once(lambda dt: self.landing_zone.reset(), 0.5)
        else:
            # Failed - return button to original parent and position
            print(f"[RESET] Button '{instance.text}' missed landing zone - returning")
            self.landing_zone.reset()
            
            # If button was reparented to FloatLayout, move it back
            if instance.parent != instance.original_parent:
                # Remove from FloatLayout
                instance.parent.remove_widget(instance)
                
                # Add back to original parent at original index
                instance.original_parent.add_widget(instance, index=instance.original_index)
                
                # Convert original window position back to parent's coordinate space
                instance.pos = instance.original_parent.to_widget(*instance.original_pos)
            else:
                # Just animate back to original position
                anim = Animation(pos=instance.original_pos, duration=0.3)
                anim.start(instance)


if __name__ == '__main__':
    DragNestedScrollDemo().run()

