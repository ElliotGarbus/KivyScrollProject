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

# TODO: Test scroll events with nested scrollviews.
# TODO: Evaluate integration of the Manager in the ScrollView.
# TODO: create feature, dwelling on a non-button widget can be turned into a scroll.
# TODO: create a test suite for the updated ScrollView & NSVM for the kivy test suite.
# TODO: test interation with draggable widgets.
# TODO: clean up code/implementation comments.
# TODO: Register the NestedScrollViewManager with kv.
# TODO: deprecate dispatch_children() and dispatch_generic in _event.pyx
# TODO: formatting prior to PR

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
        self._current_touch = None

    def _find_colliding_inner_scrollview(self, touch):
        """
        Find the first ScrollView that collides with the touch position.
        
        Optimized to check direct children first and only walk subtrees
        that collide with the touch point, avoiding unnecessary tree traversal.
        """
        viewport = self.outer_scrollview._viewport
        # Transform touch to viewport space
        touch.push()
        touch.apply_transform_2d(viewport.to_widget)

        # Iterate direct children first (instead of walking entire tree immediately)
        for child in viewport.children:
            # Quick collision check before walking subtree
            if not child.collide_point(*touch.pos):
                continue  # Skip this entire branch - touch isn't in it

            # Is this child itself a ScrollView?
            if isinstance(child, ScrollView):
                touch.pop()
                return child

            # Walk only this colliding child's subtree
            for widget in child.walk(restrict=True):
                if isinstance(widget, ScrollView) and widget.collide_point(*touch.pos):
                    touch.pop()
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
        
        # Enforce single-touch policy
        if self._current_touch is not None:
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

        # MOUSE WHEEL SPECIAL HANDLING:
        if wheel_scroll:
            # For mouse wheel events, check if we have parallel scrollviews
            if inner_scrollview:
                outer_axes = (outer_scrollview.do_scroll_x, outer_scrollview.do_scroll_y)
                inner_axes = (inner_scrollview.do_scroll_x, inner_scrollview.do_scroll_y)
                are_parallel = outer_axes == inner_axes

                if are_parallel:
                    # For parallel scrollviews, determine which one the mouse is over
                    # Check if mouse is over inner scrollview first
                    touch.pop()
                    touch.push()
                    touch.apply_transform_2d(inner_scrollview.parent.to_widget)
                    if inner_scrollview.collide_point(*touch.pos):
                        if inner_scrollview._scroll_initialize(touch):
                            touch.pop()
                            touch.grab(self)
                            touch.ud['nsvm']['mode'] = 'inner'
                            self._current_touch = touch
                            return True
                    else:
                        touch.pop()
                        touch.push()
                        touch.apply_transform_2d(outer_scrollview.parent.to_widget)
                        if outer_scrollview._scroll_initialize(touch):
                            touch.pop()
                            touch.grab(self)
                            touch.ud['nsvm']['mode'] = 'outer'
                            self._current_touch = touch
                            return True
                    touch.pop()
                    return False

            # For orthogonal scrollviews or not inner scrollview touched, outer scrollview handles the wheel
            if outer_scrollview._scroll_initialize(touch):
                touch.pop()
                touch.grab(self)
                touch.ud['nsvm']['mode'] = 'outer'
                self._current_touch = touch
                return True

        # NORMAL TOUCH HANDLING:
        # If touch is on outer scrollbar, handle it directly (don't check inner)
        if in_bar:
            if outer_scrollview._scroll_initialize(touch):
                touch.pop()
                touch.grab(self)
                touch.ud['nsvm']['mode'] = 'outer'
                self._current_touch = touch
                return True

        # First check if touch is on inner scrollview
        if inner_scrollview:
            touch.pop()
            touch.push()
            touch.apply_transform_2d(inner_scrollview.parent.to_widget)
            if inner_scrollview._scroll_initialize(touch):
                touch.pop()
                touch.grab(self)  # Manager maintains grab ownership
                touch.ud['nsvm']['mode'] = 'inner'
                self._current_touch = touch
                return True

        # If not handled by inner (or no inner), try outer scrollview
        # This handles content touches on outer scrollview
        touch.pop()
        touch.push()
        touch.apply_transform_2d(outer_scrollview.parent.to_widget)
        if outer_scrollview._scroll_initialize(touch):
            touch.pop()
            touch.grab(self)
            touch.ud['nsvm']['mode'] = 'outer'
            self._current_touch = touch
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
            # Transform touch to inner ScrollView's parent's coordinate space
            touch.push()
            touch.apply_transform_2d(self.inner_scrollview.parent.to_widget)
            result = self.inner_scrollview._scroll_update(touch)
            touch.pop()

            # If inner ScrollView rejected the touch (orthogonal movement), delegate to outer
            if not result:
                # Transform touch to outer ScrollView's parent's coordinate space
                touch.push()
                touch.apply_transform_2d(self.outer_scrollview.parent.to_widget)

                # Ensure outer ScrollView effects are initialized for scrolling
                outer_uid = self.outer_scrollview._get_uid()
                if outer_uid not in touch.ud:
                    # CRITICAL: Create touch.ud[uid] entry for outer scrollview
                    # Without this, on_scroll_move will call on_scroll_start (see line 1317-1320 in updated_sv.py)
                    # which disrupts the touch flow and causes stuck buttons
                    touch.ud[outer_uid] = {
                        'mode': 'scroll',  # Already scrolling (delegated mid-gesture)
                        'dx': 0,
                        'dy': 0,
                        'scroll_action': False,
                        'frames': 0,  # Will not be used, already a scroll
                        'can_defocus': False,  # Delegated touch shouldn't defocus
                        'time': touch.time_start,
                    }

                    # Initialize scroll effects with current touch position
                    self.outer_scrollview._initialize_scroll_effects(touch, in_bar=False)

                    # Set the active touch for outer scrollview
                    self.outer_scrollview._touch = touch

                    # Grab for outer scrollview
                    touch.grab(self.outer_scrollview)

                    # Switch mode to 'outer' - inner is now locked, all scrolling goes to outer
                    touch.ud['nsvm']['mode'] = 'outer'
                    
                    # Dispatch on_scroll_start for outer scrollview (delegation)
                    self.outer_scrollview.dispatch('on_scroll_start')

                    # Clear inner scrollview's _touch and stop its scroll effects
                    # This ensures overscroll state is cleaned up when delegating
                    if self.inner_scrollview:
                        self.inner_scrollview._touch = None
                        # Stop inner scrollview's scroll effects to reset overscroll
                        self.inner_scrollview._stop_scroll_effects(touch, not_in_bar=True)

                # Reset sv.handled flags for delegation
                touch.ud['sv.handled'] = {'x': False, 'y': False}

                # Temporarily transfer grab ownership for outer ScrollView delegation
                touch.ungrab(self)
                touch.grab(self.outer_scrollview)

                outer_result = self.outer_scrollview._scroll_update(touch)

                # Restore grab ownership to manager
                touch.ungrab(self.outer_scrollview)
                touch.grab(self)
                touch.pop()

                # CRITICAL: Always return True for delegated touches to prevent button presses
                # Even if outer ScrollView returns False, we've handled the delegation
                return True

            return result

        elif mode == 'outer':
            # Transform touch to outer ScrollView's parent's coordinate space
            touch.push()
            touch.apply_transform_2d(self.outer_scrollview.parent.to_widget)
            result = self.outer_scrollview._scroll_update(touch)
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
            
            # Clear the current touch tracking
            if self._current_touch is touch:
                self._current_touch = None

            mode = touch.ud['nsvm'].get('mode')

            if mode == 'inner' and self.inner_scrollview:
                # Transform and dispatch scroll stop
                touch.push()
                touch.apply_transform_2d(self.inner_scrollview.parent.to_widget)

                # Update effect bounds before stopping
                self.inner_scrollview._update_effect_bounds()

                uid = self.inner_scrollview._get_uid()
                if uid in touch.ud:
                    # Normal scroll stop
                    self.inner_scrollview._scroll_finalize(touch)
                    if not touch.ud[uid].get('can_defocus', True):
                        FocusBehavior.ignored_touch.append(touch)
                touch.pop()

            elif mode == 'outer' and self.outer_scrollview:
                # Transform and dispatch scroll stop
                touch.push()
                touch.apply_transform_2d(self.outer_scrollview.parent.to_widget)

                # Update effect bounds before stopping
                self.outer_scrollview._update_effect_bounds()

                uid = self.outer_scrollview._get_uid()
                if uid in touch.ud:
                    # Normal scroll stop
                    self.outer_scrollview._scroll_finalize(touch)
                    if not touch.ud[uid].get('can_defocus', True):
                        FocusBehavior.ignored_touch.append(touch)
                touch.pop()
            else:
                raise ValueError(f"Invalid mode: {mode}")
                # Still delegate to children even if mode is invalid
                return super(NestedScrollViewManager, self).on_touch_up(touch)

            # After cleaning up scroll state, always delegate to children
            # This ensures buttons/widgets get their on_touch_up even if gesture became a scroll
            # Critical for preventing stuck button states
            return super(NestedScrollViewManager, self).on_touch_up(touch)

        # For touches not managed by this manager, delegate to children
        # This is critical for button/widget interactions that aren't scroll gestures
        # Always delegate to children - this ensures buttons get their touch_up events
        # The manager only handles scroll cleanup above, everything else goes to children
        return super(NestedScrollViewManager, self).on_touch_up(touch)


if __name__ == '__main__':
    from demo_nested_orthogonal import NestedScrollViewDemo

    NestedScrollViewDemo().run()
