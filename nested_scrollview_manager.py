"""
NestedScrollViewManager for Kivy

This module provides a centralized touch routing coordinator for nested ScrollViews.
It manages touch events between outer and inner ScrollViews to prevent conflicts
and ensure proper event flow.

Key Design Decisions:
1. Touch Management: Manager grabs all touches and controls routing
2. State Tracking: Uses touch.ud keys to track nested scroll state
3. Touch Router Pattern: Centralizes all touch handling logic
4. Orthogonal Delegation: Uses sv.handled axis tracking for automatic delegation

Features:
- Automatic orthogonal scroll delegation (unhandled axes passed to outer ScrollView)
- Axis-specific coordination via sv.handled mechanism
- Simplified two-state system: 'inner' and 'outer' modes
"""

from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.clock import Clock
from updated_sv import ScrollView


class NestedScrollViewManager(RelativeLayout):
    """
    Centralized touch routing coordinator for nested ScrollViews.
    
    This manager intercepts touch events and routes them appropriately between
    outer and inner ScrollViews, preventing conflicts and ensuring proper
    event flow in nested scrolling scenarios.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer_scrollview = None
        self.inner_scrollview = None
    
    def _find_colliding_inner_scrollview(self, touch):
        """Find the first ScrollView that collides with the touch position."""
        viewport = self.outer_scrollview._viewport
        # Transform touch to viewport space
        touch.push()
        touch.apply_transform_2d(viewport.to_widget)
        
        # Walk all widgets to find ScrollViews
        for widget in viewport.walk(restrict=True):
            if isinstance(widget, ScrollView):
                collides = widget.collide_point(*touch.pos)
                if collides:
                    touch.pop()
                    print(f"Inner ScrollView found: {widget}")
                    return widget
        touch.pop()
        return None

    def on_touch_down(self, touch):
        """
        Intercept touch down events and mark them for nested management.
        
        This is the entry point for all touch handling in nested ScrollView scenarios.
        The manager grabs the touch and marks it with nested state information.
        
        Args:
            touch: The touch event to handle
            
        Returns:
            bool: True if the touch is handled by this manager
        """
        # Only handle touches that collide with this manager
        if not self.collide_point(*touch.pos):
            return False
        
        if not self.children:
            return False
            
        outer_scrollview = self.outer_scrollview = self.children[0]
        inner_scrollview = self.inner_scrollview = self._find_colliding_inner_scrollview(touch)

        # populate the touch.ud, use nsvm as the key to create a new namespace
        # mode: 'inner' or 'outer' - determines which ScrollView initially handles the touch
        # orthogonal delegation is handled via sv.handled axis tracking
        touch.ud['nsvm'] = {
            'nested_managed': self,
            'mode': None # 'inner' or 'outer'
        }

        # pass touch to outer scrollview, look for mouse wheel scroll or bar touch
        touch.push()
        touch.apply_transform_2d(outer_scrollview.parent.to_widget)
        in_bar_x, in_bar_y = outer_scrollview._check_scroll_bounds(touch)
        wheel_scroll = 'button' in touch.profile and touch.button.startswith('scroll')
        in_bar = in_bar_x or in_bar_y
        print(f"outer_scrollview:  in_bar: {in_bar}, wheel_scroll: {wheel_scroll}")
        if in_bar or wheel_scroll: 
            if outer_scrollview.dispatch('on_scroll_start', touch):
                touch.pop()
                touch.grab(self)
                touch.ud['nsvm']['mode'] = 'outer'
                print(f"Outer ScrollView accepted touch, mode set to 'outer'")
                return True
        if inner_scrollview:
            touch.pop()
            touch.push()
            touch.apply_transform_2d(inner_scrollview.parent.to_widget)
            if inner_scrollview.dispatch('on_scroll_start', touch):   
                touch.pop()
                touch.grab(self)  # Manager maintains grab ownership
                print(f"Inner ScrollView accepted touch, mode set to 'inner'")
                touch.ud['nsvm']['mode'] = 'inner'
                return True
        touch.pop()
        return False
        
    def on_touch_move(self, touch):
        """
        Handle touch movement events for nested ScrollViews.
        
        Args:
            touch: The touch event to handle
            
        Returns:
            bool: True if the touch is handled by this manager
        """
        if touch.grab_current is not self:
            return True
        print(f"NSVM: on_touch_move")
        inner_scrollview = self.inner_scrollview
        outer_scrollview = self.outer_scrollview
        mode = touch.ud['nsvm']['mode']

        # GESTURE WIDGET COORDINATION CHECK
        # =================================
        # Check if any gesture-handling widget (ScrollView or DragBehavior) has 
        # established state for this touch by looking for 'sv.' prefixed keys.
        # Both ScrollView and DragBehavior use the shared 'sv.' namespace via 
        # their _get_uid() methods to coordinate touch ownership.
        #
        # If NO 'sv.' keys exist, neither scrolling nor dragging is active,
        # so this touch should be passed to child widgets (buttons, etc.)
        # to ensure proper widget interaction.
        # TODO: Add comment to DragBehavior about this.

        if not any(isinstance(key, str) and key.startswith('sv.')
                   for key in touch.ud):
            # Handle dragged widgets - pass to children to prevent crashes
            print(f"on_touch_move: passing touch to children, no 'sv.' keys")
            if mode == 'outer':
                return outer_scrollview._delegate_to_children(touch, 'on_touch_move')
            elif mode == 'inner':
                return inner_scrollview._delegate_to_children(touch, 'on_touch_move')
            else:
                raise ValueError(f"Invalid mode: {mode}")
        
        # Initialize scroll handling state
        touch.ud['sv.handled'] = {'x': False, 'y': False}
        # Track which axes have been handled by ScrollView to prevent
        # double-processing and coordinate multi-axis scrolling
            
        if mode == 'inner':
            print(f"Moving inner ScrollView")
            # Transform touch to inner ScrollView's parent's coordinate space
            touch.push()
            touch.apply_transform_2d(self.inner_scrollview.parent.to_widget)
            result = self.inner_scrollview.dispatch('on_scroll_move', touch)
            touch.pop()
            
            # If inner ScrollView rejected the touch (orthogonal movement), delegate to outer
            if not result:
                print(f"   Inner ScrollView rejected touch, delegating to outer ScrollView")
                # Transform touch to outer ScrollView's parent's coordinate space
                touch.push()
                touch.apply_transform_2d(self.outer_scrollview.parent.to_widget)
                
                # Ensure outer ScrollView is properly initialized for scrolling
                outer_uid = self.outer_scrollview._get_uid()
                if outer_uid not in touch.ud:
                    print(f"   Initializing outer ScrollView for delegation")
                    
                    # Use the original touch start position from inner ScrollView
                    if self.inner_scrollview._touch:
                        print(f"   Using inner ScrollView start position: {self.inner_scrollview._touch.pos}")
                        # Temporarily modify touch position to the original start position
                        original_x, original_y = touch.x, touch.y
                        touch.x, touch.y = self.inner_scrollview._touch.pos
                        
                        print(f"   Initializing outer ScrollView state for delegation")
                        
                        # CRITICAL: Initialize effects BEFORE setting _touch to avoid simulate_touch_down
                        # on_scroll_start checks if self._touch is set and calls simulate_touch_down if it is
                        touch.grab(self.outer_scrollview)
                        self.outer_scrollview.dispatch('on_scroll_start', touch)
                        
                        # Set _touch AFTER on_scroll_start to avoid triggering simulate_touch_down
                        self.outer_scrollview._touch = touch
                        
                        # Restore current position
                        touch.x, touch.y = original_x, original_y
                    else:
                        # Fallback if inner ScrollView doesn't have _touch set
                        print(f"   No inner ScrollView _touch available, using current position")
                        touch.grab(self.outer_scrollview)
                        self.outer_scrollview.dispatch('on_scroll_start', touch)
                        self.outer_scrollview._touch = touch
                
                # Reset sv.handled flags for delegation
                touch.ud['sv.handled'] = {'x': False, 'y': False}
                print(f"   Reset sv.handled flags for outer ScrollView delegation")
                
                # Temporarily transfer grab ownership for outer ScrollView delegation
                touch.ungrab(self)
                touch.grab(self.outer_scrollview)
                
                outer_result = self.outer_scrollview.dispatch('on_scroll_move', touch)
                
                # Restore grab ownership to manager
                touch.ungrab(self.outer_scrollview) 
                touch.grab(self)
                touch.pop()
                
                # CRITICAL: Always return True for delegated touches to prevent button presses
                # Even if outer ScrollView returns False, we've handled the delegation
                print(f"   Outer ScrollView delegation result: {outer_result}, returning True to consume touch")
                return True
            
            return result
            
        elif mode == 'outer':
            print(f"Moving outer ScrollView")
            # Transform touch to outer ScrollView's parent's coordinate space
            touch.push()
            touch.apply_transform_2d(self.outer_scrollview.parent.to_widget)
            result = self.outer_scrollview.dispatch('on_scroll_move', touch)
            touch.pop()
            return result
        
            
        return False
        
    def on_touch_up(self, touch):
        """
        Handle touch up events and clean up nested scroll state.
        
        Args:
            touch: The touch event to handle
            
        Returns:
            bool: True if the touch is handled by this manager
        """
        if not touch.ud.get('nsvm', False):
            return False

        if touch.grab_current is not self:
            return False
        touch.ungrab(self)

        mode = touch.ud['nsvm'].get('mode')
        print(f"Touch up, mode: {mode}")
        
        if mode == 'inner' and self.inner_scrollview:
            print(f"   Cleaning up inner ScrollView")
            # Transform and dispatch scroll stop
            touch.push()
            touch.apply_transform_2d(self.inner_scrollview.parent.to_widget)
            
            # Update effect bounds before stopping
            self.inner_scrollview._update_effect_bounds()
            
            uid = self.inner_scrollview._get_uid()
            if uid in touch.ud:
                # Normal scroll stop
                self.inner_scrollview.dispatch('on_scroll_stop', touch)
                if not touch.ud[uid].get('can_defocus', True):
                    FocusBehavior.ignored_touch.append(touch)
            touch.pop()
            
        elif mode == 'outer' and self.outer_scrollview:
            print(f"   Cleaning up outer ScrollView")
            # Transform and dispatch scroll stop
            touch.push()
            touch.apply_transform_2d(self.outer_scrollview.parent.to_widget)
            
            # Update effect bounds before stopping
            self.outer_scrollview._update_effect_bounds()
            
            uid = self.outer_scrollview._get_uid()
            self.outer_scrollview.dispatch('on_scroll_stop', touch)
            if uid in touch.ud and not touch.ud[uid].get('can_defocus', True):
                FocusBehavior.ignored_touch.append(touch)
            touch.pop()
        else:
            print(f"   Invalid mode: {mode}")  # TODO: raise error?
            return False
        
        # Release grab
        return True
        
    
        
            
if __name__ == '__main__':
    from demo_NSVM import NestedScrollViewDemo
    NestedScrollViewDemo().run()
