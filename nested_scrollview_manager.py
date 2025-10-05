"""
NestedScrollViewManager for Kivy

This module provides a centralized touch routing coordinator for nested ScrollViews.
It manages touch events between outer and inner ScrollViews to prevent conflicts
and ensure proper event flow.

Key Design Decisions:
1. Touch Management: controls touch routing between outer and inner ScrollViews
2. State Tracking: Uses touch.ud keys to track nested scroll state
3. Touch Router Pattern: Centralizes all touch handling logic
4. Orthogonal Delegation: Uses sv.handled axis tracking for automatic delegation

Mouse wheel scrolling behavior: 
- For orthogonal ScrollViews Mouse wheel scrolling is handled by the scrollview
  that matches the direction of the scroll wheel.
- For parallel ScrollViews Mouse wheel scrolling is handled by the scrollview
  the mouse is touching.  Scrolling is not propagated to the other scrollview.

Content Touch scrolling behavior:
- For orthogonal ScrollViews Touch scrolling is handled by the scrollview
  that matches the direction of the touch.
- For parallel ScrollViews Touch scrolling is handled by the scrollview
  that is touched.  When scrolling the inner scrollview 
  hits its boundary the scroll is propagated to the outer scrollview.

Scrollbar scrolling behavior:
- For parallel scrollviwes the inner scrollbar does not propagate scroll to the outer scrollview.
"""

#TODO: update scroll_events so they work as expected.
#TODO: Evaluate integration of the Manager in the ScrollView.
#TODO: create feature, dwelling on a non-button widget can be turned into a scroll.
#TODO: create a test suite for the updated ScrollView & NSVM for the kivy test suite.
#TODO: test interation with draggable widgets. 
#TODO: remove debug print statements.
#TODO: clean up code/implementation comments.
#TODO: Register the NestedScrollViewManager with kv.
#TODO: deprecate dispatch_children() and dispatch_generic in _event.pyx (search for use)
#TODO: formatting prior to PR

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty
from updated_sv import ScrollView


class NestedScrollViewManager(RelativeLayout):
    """
    Centralized touch routing coordinator for nested ScrollViews.
    
    This manager intercepts touch events and routes them appropriately between
    outer and inner ScrollViews, preventing conflicts and ensuring proper
    event flow in nested scrolling scenarios.
    """
    
    parallel_delegation = BooleanProperty(True)
    """
    Controls boundary delegation for parallel nested ScrollViews.
    
    When True (web-style):
    - Touch starting at inner boundary, moving away from boundary → delegates to outer scrollview
    - else → scrolls inner only, never delegates
    
    When False (default):
    - No delegation, only touched scrollview scrolls
    - Inner scrollview shows overscroll effects at boundaries
    - Touch stays with initially touched scrollview for entire gesture
    
    Default: False (no boundary delegation)
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
        # delegation_mode: tracks web-style boundary delegation state
        #   - 'unknown': touch did not start at boundary
        #   - 'start_at_boundary': touch started at boundary, may delegate
        #   - 'locked': delegating to outer, inner locked
        # orthogonal delegation is handled via sv.handled axis tracking
        touch.ud['nsvm'] = {
            'nested_managed': self,
            'mode': None,  # 'inner' or 'outer'
            'delegation_mode': 'unknown'  # Will be set in ScrollView.on_scroll_start
        }

        touch.push()
        touch.apply_transform_2d(outer_scrollview.parent.to_widget)
        in_bar_x, in_bar_y = outer_scrollview._check_scroll_bounds(touch)
        wheel_scroll = 'button' in touch.profile and touch.button.startswith('scroll')
        in_bar = in_bar_x or in_bar_y
        print(f"outer_scrollview:  in_bar: {in_bar}, wheel_scroll: {wheel_scroll}")
        
        # MOUSE WHEEL SPECIAL HANDLING:
        if wheel_scroll:
            # For mouse wheel events, check if we have parallel scrollviews
            if inner_scrollview:
                outer_axes = (outer_scrollview.do_scroll_x, outer_scrollview.do_scroll_y)
                inner_axes = (inner_scrollview.do_scroll_x, inner_scrollview.do_scroll_y)
                are_parallel = outer_axes == inner_axes
                
                if are_parallel:
                    print(f"Parallel scrollviews detected - using position-based wheel routing")
                    # For parallel scrollviews, determine which one the mouse is over
                    # Check if mouse is over inner scrollview first
                    touch.pop()
                    touch.push()
                    touch.apply_transform_2d(inner_scrollview.parent.to_widget)
                    if inner_scrollview.collide_point(*touch.pos):
                        print(f"Mouse wheel over inner scrollview - routing to inner")
                        if inner_scrollview.dispatch('on_scroll_start', touch):
                            touch.pop()
                            touch.grab(self)
                            touch.ud['nsvm']['mode'] = 'inner'
                            print(f"Inner ScrollView accepted wheel touch, mode set to 'inner'")
                            return True
                    else:
                        print(f"Mouse wheel over outer scrollview - routing to outer")
                        touch.pop()
                        touch.push()
                        touch.apply_transform_2d(outer_scrollview.parent.to_widget)
                        if outer_scrollview.dispatch('on_scroll_start', touch):
                            touch.pop()
                            touch.grab(self)
                            touch.ud['nsvm']['mode'] = 'outer'
                            print(f"Outer ScrollView accepted wheel touch, mode set to 'outer'")
                            return True
                    touch.pop()
                    return False
            
            # For orthogonal scrollviews or not inner scrollview touched, outer scrollview handles the wheel
            if outer_scrollview.dispatch('on_scroll_start', touch):
                touch.pop()
                touch.grab(self)
                touch.ud['nsvm']['mode'] = 'outer'
                print(f"Outer ScrollView accepted wheel touch, mode set to 'outer'")
                return True
        
        # NORMAL TOUCH HANDLING:
        # If touch is on outer scrollbar, handle it directly (don't check inner)
        if in_bar:
            print(f"Touch on outer scrollbar - routing directly to outer")
            if outer_scrollview.dispatch('on_scroll_start', touch):
                touch.pop()
                touch.grab(self)
                touch.ud['nsvm']['mode'] = 'outer'
                print(f"Outer ScrollView accepted bar touch, mode set to 'outer'")
                return True
        
        # First check if touch is on inner scrollview
        if inner_scrollview:
            touch.pop()
            touch.push()
            touch.apply_transform_2d(inner_scrollview.parent.to_widget)
            if inner_scrollview.dispatch('on_scroll_start', touch):   
                touch.pop()
                touch.grab(self)  # Manager maintains grab ownership
                print(f"Inner ScrollView accepted touch, mode set to 'inner'")
                touch.ud['nsvm']['mode'] = 'inner'
                print(f"  delegation_mode is now: '{touch.ud['nsvm']['delegation_mode']}'")
                return True
        
        # If not handled by inner (or no inner), try outer scrollview
        # This handles content touches on outer scrollview
        touch.pop()
        touch.push()
        touch.apply_transform_2d(outer_scrollview.parent.to_widget)
        if outer_scrollview.dispatch('on_scroll_start', touch):
            touch.pop()
            touch.grab(self)
            touch.ud['nsvm']['mode'] = 'outer'
            print(f"Outer ScrollView accepted touch, mode set to 'outer'")
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
                
                # Ensure outer ScrollView effects are initialized for scrolling
                outer_uid = self.outer_scrollview._get_uid()
                if outer_uid not in touch.ud:
                    print(f"   Initializing outer ScrollView effects for delegation")
                    
                    # Initialize scroll effects with current touch position
                    # Touch state (dx, dy, mode, etc.) is already set up - we just need effects
                    self.outer_scrollview._initialize_scroll_effects(touch, in_bar=False)
                    
                    # Set the active touch for outer scrollview
                    self.outer_scrollview._touch = touch
                    
                    # Grab for outer scrollview
                    touch.grab(self.outer_scrollview)
                    
                    # Switch mode to 'outer' - inner is now locked, all scrolling goes to outer
                    touch.ud['nsvm']['mode'] = 'outer'
                    print(f"   Switched mode to 'outer' (inner locked, outer scrolling)")
                    
                    # Clear inner scrollview's _touch since it's no longer actively scrolling
                    if self.inner_scrollview:
                        self.inner_scrollview._touch = None
                        print(f"   Cleared inner ScrollView._touch")
                
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
            bool: True if the touch is handled by this manager or its children
        """
        # First, handle touches that this manager is actively managing
        if touch.ud.get('nsvm', False) and touch.grab_current is self:
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
                if uid in touch.ud:
                    # Normal scroll stop
                    self.outer_scrollview.dispatch('on_scroll_stop', touch)
                    if not touch.ud[uid].get('can_defocus', True):
                        FocusBehavior.ignored_touch.append(touch)
                touch.pop()
            else:
                print(f"   Invalid mode: {mode}")  # TODO: raise error?
                return False
                
            return True
        
        # For touches not managed by this manager, delegate to children
        # This is critical for button/widget interactions that aren't scroll gestures
        # Always delegate to children - this ensures buttons get their touch_up events
        # The manager only handles scroll cleanup above, everything else goes to children
        return super(NestedScrollViewManager, self).on_touch_up(touch)
        
    
        
            
if __name__ == '__main__':
    from demo_nested_orthogonal import NestedScrollViewDemo
    NestedScrollViewDemo().run()
