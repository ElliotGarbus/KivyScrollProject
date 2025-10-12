"""
Test to check if 'svavoid' is used to coordinate between ScrollView and DragBehavior.

SUMMARY OF BEHAVIOR:
===================

Both ScrollView and DragBehavior use a "delayed grab" pattern with identical logic:

SHARED PATTERN:
- Timeout: Both use 55ms default (scroll_timeout / drag_timeout)
- Distance: Both use 20px default (scroll_distance / drag_distance)  
- Decision: Wait to determine if touch is a gesture (scroll/drag) or click
- Grab: Only grab touch after confirming it's a gesture
- Delegate: If timeout expires without gesture, ungrab and re-dispatch to children

SVAVOID PURPOSE (Per-Widget, No Cross-Widget Coordination):
- Each widget has its own UID-namespaced svavoid key (e.g., svavoid.123)
- Set in on_touch_down when widget determines "this touch is not for me"
- Checked in on_touch_move and on_touch_up to skip processing
- Acts as optimization: avoids re-checking collision/state on every move event
- IS NOT used for coordination between widgets

ACTUAL COORDINATION MECHANISM:
- Primary: Kivy's touch grab system (touch.grab(), grab_current, grab_list)
- Secondary: Widget hierarchy and on_touch_* return values
- When DragBehavior grabs → ScrollView never processes the touch
- When DragBehavior doesn't grab → touch propagates to ScrollView

This test demonstrates:
1. Each widget checks only its OWN svavoid key (different UIDs)
2. Dragging works without triggering scrolling (via grab system)
3. Scrolling works when not touching draggable areas (touch propagation)
4. svavoid is for per-widget state tracking, not inter-widget coordination

Console output shows the touch.ud keys being set and checked with their UIDs.
"""

from kivy.app import App
from kivy.uix.scrollview import ScrollView as KivyScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import DragBehavior
from kivy.core.window import Window


class InstrumentedDragButton(DragBehavior, Button):
    """DragBehavior button with instrumentation to show svavoid coordination."""
    
    def __init__(self, **kwargs):
        # Set drag properties in kwargs before super().__init__
        kwargs['drag_timeout'] = 10000000  # Very long timeout so drag always works
        kwargs['drag_distance'] = 10
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (150, 60)
        self.pos = (20, 20)
        # Initialize drag_rectangle - will be updated by bind
        self.drag_rectangle = [0, 0, 150, 60]
        
    def _get_uid(self, prefix='sv'):
        return '{0}.{1}'.format(prefix, self.uid)
    
    def on_touch_down(self, touch):
        xx, yy, w, h = self.drag_rectangle
        x, y = touch.pos
        
        # Check if touch collides with this widget
        if not self.collide_point(x, y):
            # DragBehavior sets svavoid when NOT on draggable area
            touch.ud[self._get_uid('svavoid')] = True
            print(f"  [DragButton] Touch NOT on button at {touch.pos}")
            print(f"  [DragButton] SET svavoid.{self.uid} = True")
            print(f"  [DragButton] -> Signals ScrollView to proceed with scrolling")
            return super(DragBehavior, self).on_touch_down(touch)
        
        print(f"  [DragButton] Touch ON button at {touch.pos}")
        print(f"  [DragButton] DID NOT set svavoid -> Will try to drag")
        
        # Normal DragBehavior logic
        if self._drag_touch or ('button' in touch.profile and
                                touch.button.startswith('scroll')) or\
                not ((xx < x <= xx + w) and (yy < y <= yy + h)):
            return super(DragBehavior, self).on_touch_down(touch)
        
        self._drag_touch = touch
        uid = self._get_uid()
        touch.grab(self)
        print(f"  [DragButton] Grabbed touch, uid={uid}")
        touch.ud[uid] = {
            'mode': 'unknown',
            'dx': 0,
            'dy': 0}
        return True
    
    def on_touch_move(self, touch):
        if self._get_uid('svavoid') in touch.ud or\
                self._drag_touch is not touch:
            return super(DragBehavior, self).on_touch_move(touch) or\
                self._get_uid() in touch.ud
        if touch.grab_current is not self:
            return True
        
        uid = self._get_uid()
        ud = touch.ud[uid]
        mode = ud['mode']
        if mode == 'unknown':
            ud['dx'] += abs(touch.dx)
            ud['dy'] += abs(touch.dy)
            from kivy.metrics import sp
            if ud['dx'] > sp(self.drag_distance):
                mode = 'drag'
                print(f"  [DragButton] DRAG MODE activated (dx={ud['dx']:.1f})")
            if ud['dy'] > sp(self.drag_distance):
                mode = 'drag'
                print(f"  [DragButton] DRAG MODE activated (dy={ud['dy']:.1f})")
            ud['mode'] = mode
        if mode == 'drag':
            self.x += touch.dx
            self.y += touch.dy
        return True
    
    def on_touch_up(self, touch):
        if self._get_uid('svavoid') in touch.ud:
            return super(DragBehavior, self).on_touch_up(touch)
        
        if self._drag_touch and self in [x() for x in touch.grab_list]:
            touch.ungrab(self)
            print(f"  [DragButton] Released touch")
            self._drag_touch = None
            uid = self._get_uid()
            ud = touch.ud[uid]
            if ud['mode'] == 'unknown':
                print(f"  [DragButton] Was a CLICK, not drag")
                super(DragBehavior, self).on_touch_down(touch)
        else:
            if self._drag_touch is not touch:
                super(DragBehavior, self).on_touch_up(touch)
        return self._get_uid() in touch.ud


class InstrumentedScrollView(KivyScrollView):
    """ScrollView with instrumentation to show svavoid coordination."""
    
    def _get_uid(self, prefix='sv'):
        return '{0}.{1}'.format(prefix, self.uid)
    
    def on_scroll_start(self, touch, check_children=True):
        svavoid_key = self._get_uid('svavoid')
        
        # Handle mouse wheel events normally without instrumentation
        if 'button' in touch.profile and touch.button.startswith('scroll'):
            return super().on_scroll_start(touch, check_children)
        
        if check_children:
            touch.push()
            touch.apply_transform_2d(self.to_local)
            if self.dispatch_children('on_scroll_start', touch):
                touch.pop()
                return True
            touch.pop()
        
        if not self.collide_point(*touch.pos):
            touch.ud[svavoid_key] = True
            print(f"  [ScrollView] Touch outside bounds, SET svavoid.{self.uid} = True")
            return
        
        # Check if svavoid was set by DragBehavior
        if svavoid_key in touch.ud:
            print(f"  [ScrollView] FOUND svavoid.{self.uid} = True")
            print(f"  [ScrollView] -> Skipping scroll processing (DragBehavior signaled to avoid)")
            return
        
        print(f"  [ScrollView] svavoid NOT found")
        print(f"  [ScrollView] -> Proceeding with scroll initialization")
        
        if self.disabled:
            return True
        if self._touch or (not (self.do_scroll_x or self.do_scroll_y)):
            return self.simulate_touch_down(touch)
        
        # Rest of scroll initialization...
        return super().on_scroll_start(touch, check_children=False)
    
    def on_scroll_move(self, touch):
        # Handle mouse wheel events normally without instrumentation
        if 'button' in touch.profile and touch.button.startswith('scroll'):
            return super().on_scroll_move(touch)
        
        svavoid_key = self._get_uid('svavoid')
        if svavoid_key in touch.ud:
            print(f"  [ScrollView] on_scroll_move: Found svavoid, returning False")
            return False
        
        uid = self._get_uid()
        if uid in touch.ud:
            ud = touch.ud[uid]
            if ud.get('mode') == 'scroll':
                print(f"  [ScrollView] SCROLLING (mode=scroll)")
        
        return super().on_scroll_move(touch)
    
    def on_scroll_stop(self, touch, check_children=True):
        # Handle mouse wheel events normally without instrumentation
        if 'button' in touch.profile and touch.button.startswith('scroll'):
            return super().on_scroll_stop(touch, check_children)
        
        svavoid_key = self._get_uid('svavoid')
        if svavoid_key in touch.ud:
            print(f"  [ScrollView] on_scroll_stop: Found svavoid, skipping")
            return
        
        return super().on_scroll_stop(touch, check_children)


class TestSvavoidApp(App):
    def build(self):
        Window.size = (900, 600)
        
        # Main layout
        root = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        
        # Left side: Instructions
        left_panel = BoxLayout(orientation='vertical', size_hint=(0.4, 1), spacing=5)
        
        title = Label(
            text='[b]svavoid Coordination Test[/b]',
            markup=True,
            size_hint=(1, None),
            height=40,
            font_size='18sp'
        )
        
        instructions = Label(
            text=(
                '[b]Test Cases:[/b]\n\n'
                '1. [b]Drag the BLUE button[/b]\n'
                '   • Touch ON button\n'
                '   • svavoid NOT set\n'
                '   • Button drags\n'
                '   • No scrolling\n\n'
                '2. [b]Touch EMPTY SPACE[/b]\n'
                '   • Touch NOT on button\n'
                '   • DragButton sets svavoid\n'
                '   • ScrollView reads svavoid\n'
                '   • ScrollView scrolls\n\n'
                '3. [b]Touch GRAY buttons[/b]\n'
                '   • Normal button behavior\n'
                '   • No svavoid involvement\n\n'
                '[b]Watch console output[/b]\n'
                'to see the coordination!'
            ),
            markup=True,
            size_hint=(1, 1),
            text_size=(None, None),
            halign='left',
            valign='top',
            padding=(10, 10)
        )
        instructions.bind(size=lambda *x: setattr(instructions, 'text_size', (instructions.width - 20, None)))
        
        left_panel.add_widget(title)
        left_panel.add_widget(instructions)
        
        # Right side: Split into middle (ScrollView) and right (Drag button area)
        right_container = BoxLayout(orientation='horizontal', size_hint=(0.6, 1), spacing=10)
        
        # Middle section: ScrollView
        scroll_container = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
        
        # Create scrollable content
        content = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=10
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Add some regular buttons
        for i in range(15):
            btn = Button(
                text=f'Regular Button {i+1}',
                size_hint_y=None,
                height=50,
                background_color=(0.5, 0.5, 0.5, 1)
            )
            btn.bind(on_press=lambda x, i=i: print(f"\n[Button {i+1}] Clicked!"))
            content.add_widget(btn)
        
        # Create ScrollView
        scroll_view = InstrumentedScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width='10dp'
        )
        scroll_view.add_widget(content)
        scroll_container.add_widget(scroll_view)
        
        # Right section: Draggable button area
        drag_area = FloatLayout(size_hint=(0.4, 1))
        
        # Add draggable button (NO pos_hint - set pos after layout)
        drag_button = InstrumentedDragButton(
            text='DRAG ME\n(Draggable)',
            background_color=(0.2, 0.5, 0.8, 1)
        )
        
        # Update drag_rectangle when button moves
        def update_drag_rect(instance, *args):
            instance.drag_rectangle = [instance.x, instance.y, instance.width, instance.height]
        
        drag_button.bind(pos=update_drag_rect, size=update_drag_rect)
        
        # Set initial position after layout settles
        # from kivy.clock import Clock
        # def set_initial_pos(dt):
        #     # Position button on right side of drag_area
        #     print(f'{right_container.pos} right_container.size={right_container.size}')
        #     drag_button.right = right_container.right
        #     drag_button.center_y = right_container.height * 0.7
        #     update_drag_rect(drag_button)
        
        # Clock.schedule_once(set_initial_pos, 1)
        
        drag_area.add_widget(drag_button)
        
        # Assemble right container
        right_container.add_widget(scroll_container)
        right_container.add_widget(drag_area)
        
        root.add_widget(left_panel)
        root.add_widget(right_container)
        
        print("\n" + "="*70)
        print("svavoid COORDINATION TEST - Ready")
        print("="*70)
        print("\nTry these actions and watch the console output:")
        print("1. Drag the BLUE button")
        print("2. Touch empty space in the ScrollView area")
        print("3. Click gray buttons")
        print("="*70 + "\n")
        
        return root


if __name__ == '__main__':
    TestSvavoidApp().run()

