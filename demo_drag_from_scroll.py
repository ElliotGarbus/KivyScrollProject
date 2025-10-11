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
from updated_sv import ScrollView


class DraggableButton(DragBehavior, Button):
    """Button that can be dragged from the ScrollView to a landing zone."""
    dragging = BooleanProperty(False)
    original_pos = ListProperty([0, 0])
    original_parent = None
    float_parent = None  # Will hold reference to FloatLayout for reparenting
    original_index = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set drag properties
        self.drag_timeout = 100
        self.drag_distance = 20
        # Bind to update drag_rectangle when position/size changes
        self.bind(pos=self.update_drag_rectangle, size=self.update_drag_rectangle)
    
    def update_drag_rectangle(self, *args):
        """Update drag_rectangle to match button's current position and size."""
        self.drag_rectangle = [self.x, self.y, self.width, self.height]
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Store original position in window coordinates
            self.original_pos = self.to_window(*self.pos)
            self.original_parent = self.parent
            self.original_index = self.parent.children.index(self)
            print(f'Touch down on button "{self.text}" at {touch.pos}')
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if touch.grab_current is self:
            # On first move, reparent to FloatLayout so button appears on top
            if not self.dragging and self.float_parent and self.parent != self.float_parent:
                # Convert position to window coordinates before reparenting
                window_pos = self.to_window(*self.pos)
                
                # Remove from original parent
                self.parent.remove_widget(self)
                
                # Add to FloatLayout
                self.float_parent.add_widget(self)
                
                # Set position in FloatLayout's coordinate space
                self.pos = self.float_parent.to_widget(*window_pos)
                
                print(f'Reparented button "{self.text}" to FloatLayout')
            
            self.opacity = 0.6
            self.dragging = True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.dragging:
            self.opacity = 1
            self.dragging = False
            print(f'Touch up on button "{self.text}", dragging was True')
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
        
        print(f"[DRAG] Button '{instance.text}' drag completed")
        print(f"[DRAG] Touch position: {touch.pos}")
        
        # Use touch position directly to check collision with landing zone
        # Transform touch position to landing zone's coordinate space
        touch.push()
        touch.apply_transform_2d(self.landing_zone.to_widget)
        collision = self.landing_zone.collide_point(*touch.pos)
        touch.pop()
        
        print(f"[DRAG] Landing zone bounds (local): pos={self.landing_zone.pos}, size={self.landing_zone.size}")
        print(f"[DRAG] Collision check: {collision}")
        
        if collision:
            # Success! Button dropped in landing zone
            print(f"[SUCCESS] Button '{instance.text}' dropped in landing zone - REMOVING")
            self.landing_zone.set_success()
            
            # Remove the button from the scroll content
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
    DragFromScrollDemo().run()

