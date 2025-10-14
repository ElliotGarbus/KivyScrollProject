"""
demo_drag_over_scroll.py

Demo testing DragBehavior interaction with ScrollView.
Tests that dragging a button over a scrolling area doesn't cause issues.

Layout:
- Center: Vertical ScrollView with buttons
- Right: Draggable button (with DragBehavior)
- Far right: Landing zone that changes color when button is dropped in it
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
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from updated_sv import ScrollView


class DraggableButton(DragBehavior, Button):
    """Button that can be dragged around the screen."""
    dragging = BooleanProperty(False)
    original_pos = ListProperty([0, 0])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set drag properties
        self.drag_timeout = 10000000
        self.drag_distance = 20
        # Bind to update drag_rectangle when position/size changes
        self.bind(pos=self.update_drag_rectangle, size=self.update_drag_rectangle)
    
    def update_drag_rectangle(self, *args):
        """Update drag_rectangle to match button's current position and size."""
        self.drag_rectangle = [self.x, self.y, self.width, self.height]
        print(f"drag_rectangle updated: {self.drag_rectangle}")
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print(f'on touch down at {touch.pos}')
            self.original_pos = self.pos[:]
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.opacity = 0.6
            self.dragging = True
            print(f'on touch move, dragging, pos={self.pos}')
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.dragging:
            self.opacity = 1
            self.dragging = False
            print(f'on touch up, dragging was True')
        return super().on_touch_up(touch)


class LandingZone(Widget):
    """Visual landing zone that changes color when draggable button is dropped in it."""
    
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
            text='Landing\nZone',
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
        # Update label position to match
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


class DragOverScrollDemo(App):
    def build(self):
        # Root layout
        root = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Title at top
        title = Label(
            text='[b]Drag Over ScrollView Test[/b]\n'
                 'Drag the button to the landing zone (passes over scrollview)',
            markup=True,
            size_hint=(1, None),
            height=dp(60)
        )
        root.add_widget(title)
        
        # Main content area (below title) - use FloatLayout for absolute positioning of draggable button
        main_area = FloatLayout(size_hint=(1, 1))
        
        # Background BoxLayout for the structured content
        content_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            padding=dp(10),
            size_hint=(1, 1)
        )
        
        # Left margin (20%)
        left_margin = Widget(size_hint_x=0.2)
        content_layout.add_widget(left_margin)
        
        # Center: Vertical ScrollView with buttons (30%)
        scrollview_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.3
        )
        
        sv_label = Label(
            text='Scrollable Buttons',
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        scrollview_container.add_widget(sv_label)
        
        scrollview = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10,
            size_hint=(1, 1)
        )
        
        # ScrollView content
        sv_content = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        sv_content.bind(minimum_height=sv_content.setter('height'))
        
        # Add 20 buttons to scrollview
        for i in range(20):
            btn = Button(
                text=f'Button {i+1}',
                size_hint_y=None,
                height=dp(50),
                background_color=[0.2, 0.4, 0.8, 1]
            )
            sv_content.add_widget(btn)
        
        scrollview.add_widget(sv_content)
        scrollview_container.add_widget(scrollview)
        content_layout.add_widget(scrollview_container)
        
        # Middle space (15%)
        middle_space = Widget(size_hint_x=0.15)
        content_layout.add_widget(middle_space)
        
        # Draggable button area (15%)
        drag_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.15
        )
        
        drag_label = Label(
            text='Drag Me -',
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        drag_container.add_widget(drag_label)
        
        # This is just for spacing in the BoxLayout
        drag_container.add_widget(Widget(size_hint_y=0.4))
        
        content_layout.add_widget(drag_container)
        
        # Landing zone (20%)
        landing_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.2
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
        
        # Add content layout to main area
        main_area.add_widget(content_layout)
        
        # Create draggable button (position it absolutely in FloatLayout)
        self.draggable_btn = DraggableButton(
            text='Drag Me!',
            size_hint=(None, None),
            size=(dp(120), dp(80)),
            background_color=[0.8, 0.3, 0.3, 1]
        )
        
        main_area.add_widget(self.draggable_btn)
        
        # Set initial position after adding to parent (so we know parent size)
        from kivy.clock import Clock
        def set_initial_pos(dt):
            # Position in the drag area (center-right)
            self.draggable_btn.pos = (
                main_area.width * 0.65 - self.draggable_btn.width / 2,
                main_area.height * 0.5 - self.draggable_btn.height / 2
            )
            print(f"Initial position set: {self.draggable_btn.pos}")
        Clock.schedule_once(set_initial_pos, 0.1)
        
        # Bind to drag release
        self.draggable_btn.bind(on_touch_up=self.on_button_release)
        self.draggable_btn.bind(pos=self.on_button_move)
        
        # Add main area to root
        root.add_widget(main_area)
        
        return root
    
    def on_button_move(self, instance, pos):
        """Called when button is being dragged - check for hover over landing zone."""
        # Check if button center is over landing zone
        btn_center_x = instance.center_x
        btn_center_y = instance.center_y
        
        if self.landing_zone.collide_point(btn_center_x, btn_center_y):
            self.landing_zone.set_hover(True)
        else:
            self.landing_zone.reset()
    
    def on_button_release(self, instance, touch):
        """Called when button is released - check if in landing zone."""
        if not instance.collide_point(*touch.pos):
            return
        
        # Check if button center is in landing zone
        btn_center_x = instance.center_x
        btn_center_y = instance.center_y
        
        if self.landing_zone.collide_point(btn_center_x, btn_center_y):
            # Success! Dropped in landing zone
            self.landing_zone.set_success()
            instance.background_color = [0.1, 0.8, 0.1, 1]  # Green
            print("[SUCCESS] Button dropped in landing zone!")
        else:
            # Failed - reset landing zone
            self.landing_zone.reset()
            instance.background_color = [0.8, 0.3, 0.3, 1]  # Red
            print("[RESET] Button returned to start position")
        
        # Always return button to start position after drop
        from kivy.clock import Clock
        def return_to_start(dt):
            instance.pos = instance.original_pos
            # Reset colors after a delay
            def reset_colors(dt):
                instance.background_color = [0.8, 0.3, 0.3, 1]
                self.landing_zone.reset()
            Clock.schedule_once(reset_colors, 1.0)
        
        Clock.schedule_once(return_to_start, 0.5)


if __name__ == '__main__':
    DragOverScrollDemo().run()

