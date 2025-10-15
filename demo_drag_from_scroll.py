"""
demo_drag_from_scroll.py

Demo showing dragging buttons OUT of a ScrollView to a landing zone.
Tests that DragBehavior works correctly with buttons inside a ScrollView.

Features:
- Scrollable list of draggable buttons
- Drag buttons from the list to the landing zone
- Buttons that hit the landing zone are removed from the list
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
    """Button that can be dragged from the ScrollView to a landing zone."""
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
        # Set drag properties - use timeout to prevent auto-grab
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


class DragFromScrollDemo(App):
    def build(self):
        # Root layout
        root = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Title
        title = Label(
            text='[b]Drag From ScrollView Demo[/b]\n'
                 'Drag buttons from the list to the drop zone to remove them',
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
        
        # Left side: Landing zone (40%) - First in widget tree so it's below dragged buttons
        landing_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.4
        )
        
        landing_label = Label(
            text='Drop Here to Remove',
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        landing_container.add_widget(landing_label)
        
        self.landing_zone = LandingZone(size_hint=(1, 1))
        landing_container.add_widget(self.landing_zone)
        
        content_layout.add_widget(landing_container)
        
        # Right side: ScrollView with draggable buttons (60%)
        scroll_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.6
        )
        
        scroll_label = Label(
            text='Draggable Items (scroll to see more)',
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        scroll_container.add_widget(scroll_label)
        
        self.scrollview = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(10),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10,
            size_hint=(1, 1)
        )
        
        # ScrollView content - vertical list
        self.scroll_content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        self.scroll_content.bind(minimum_height=self.scroll_content.setter('height'))
        
        # Add 20 draggable buttons to the list
        for i in range(20):
            btn = DraggableButton(
                text=f'Item {i+1}',
                size_hint_y=None,
                height=dp(60),
                background_color=[0.2 + (i * 0.04) % 0.6, 0.4, 0.8, 1]
            )
            # Set reference to FloatLayout for reparenting during drag
            btn.float_parent = main_area
            # Bind to handle drag completion
            btn.bind(on_touch_up=self.on_button_drag_complete)
            self.scroll_content.add_widget(btn)
        
        self.scrollview.add_widget(self.scroll_content)
        scroll_container.add_widget(self.scrollview)
        content_layout.add_widget(scroll_container)
        
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
        
        # Check if button was dropped in landing zone
        touch.push()
        touch.apply_transform_2d(self.landing_zone.to_widget)
        collision = self.landing_zone.collide_point(*touch.pos)
        touch.pop()
        
        if collision:
            # Success! Remove button
            self.landing_zone.set_success()
            if instance.parent:
                instance.parent.remove_widget(instance)
            Clock.schedule_once(lambda dt: self.landing_zone.reset(), 0.5)
        else:
            # Failed - return button to original position
            self.landing_zone.reset()
            if instance.parent != instance.original_parent:
                instance.parent.remove_widget(instance)
                instance.original_parent.add_widget(instance, index=instance.original_index)
                instance.pos = instance.original_parent.to_widget(*instance.original_pos)
            else:
                anim = Animation(pos=instance.original_pos, duration=0.3)
                anim.start(instance)


if __name__ == '__main__':
    DragFromScrollDemo().run()

