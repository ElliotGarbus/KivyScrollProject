'''
NestedScrollViewManager
=======================

.. versionadded:: 3.0.0

The :class:`NestedScrollViewManager` widget provides coordination for nested 
:class:`~kivy.uix.scrollview.ScrollView` configurations. It manages touch event 
routing between outer and inner ScrollViews to provide intuitive scrolling 
behavior in nested scenarios.


Usage Requirements
------------------

The NestedScrollViewManager supports two levels of scrolling: one outer 
ScrollView and one or more inner ScrollViews. The outer ScrollView must be 
the direct child of the NestedScrollViewManager. 

In KV, it will look something like this:

NestedScrollViewManager:
    ScrollView:  # the outer scrollview
        ...attributes and layout
        ...
        ...ScrollView:  # one or more scrollviews deeper in the widget tree


Nested Scrolling Behavior
-------------------------

The NestedScrollViewManager automatically detects the scrolling configuration 
and applies appropriate behavior:

**Orthogonal Scrolling** (outer and inner scroll in different directions):
    - Touch scrolling: Each ScrollView handles touches in its scroll direction
    - Mouse wheel: Scrolls the ScrollView matching the wheel direction
    - Example: Vertical outer + Horizontal inner

**Parallel Scrolling** (outer and inner scroll in the same direction):
    - Touch scrolling: Uses web-style boundary delegation (see below)
    - Mouse wheel: Scrolls only the ScrollView under the mouse cursor
    - Scrollbar: Does not propagate scroll to the other ScrollView
    - Example: Vertical outer + Vertical inner

**Mixed Scrolling** (outer scrolls XY, inner scrolls single axis, or vice versa):
    - Shared axis: Uses web-style boundary delegation
    - Exclusive axes: Immediate delegation or inner-only scrolling
    - Mouse wheel: Routes based on axis configuration
    - Example: XY outer + Horizontal inner


Web-Style Boundary Delegation
------------------------------

For parallel and shared-axis scrolling, the manager implements web-style 
delegation behavior:

    - Touch starts at inner boundary, moves away → delegates to outer immediately
    - Touch starts at inner boundary, moves inward → scrolls inner only
    - Touch starts not at boundary → scrolls inner only, never delegates 
      (even when reaching boundary mid-gesture)
    - New touch required at boundary to delegate to outer

This behavior can be disabled by setting :attr:`parallel_delegation` to False.


Python Example (Orthogonal Nesting)::
-------------------------------------

    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from nested_scrollview_manager import NestedScrollViewManager


    class NestedScrollApp(App):
        def build(self):
            # Create the NestedScrollViewManager (parent of outer ScrollView)
            manager = NestedScrollViewManager()
            
            # Create outer vertical ScrollView
            outer_sv = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
                smooth_scroll_end=10,
                bar_width='10dp',
                scroll_type=['bars', 'content']
            )
            
            # Outer content layout (MUST be a Layout widget)
            outer_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=20
            )
            outer_layout.bind(minimum_height=outer_layout.setter('height'))
            
            # Add several horizontal ScrollViews
            for i in range(5):
                # Create nested horizontal ScrollView
                inner_sv = ScrollView(
                    do_scroll_x=True,
                    do_scroll_y=False,
                    size_hint_y=None,
                    height=120,
                    smooth_scroll_end=10,
                    bar_width='10dp',
                    scroll_type=['bars', 'content']
                )
                
                # Inner content layout
                inner_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_x=None,
                    spacing=10
                )
                inner_layout.bind(minimum_width=inner_layout.setter('width'))
                
                # Add horizontal scrolling buttons
                for j in range(10):
                    btn = Button(
                        text=f'Button {i}-{j}',
                        size_hint_x=None,
                        width=100,
                        height=80
                    )
                    inner_layout.add_widget(btn)
                
                # Assemble inner ScrollView
                inner_sv.add_widget(inner_layout)
                outer_layout.add_widget(inner_sv)
            
            # Assemble the nested structure
            outer_sv.add_widget(outer_layout)
            manager.add_widget(outer_sv)
            
            return manager


    if __name__ == '__main__':
        NestedScrollApp().run()


KV Example (Orthogonal Nesting)
------------------------------

    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.properties import NumericProperty

    KV = """
    <HorizontalScrollRow>:
        do_scroll_x: True
        do_scroll_y: False
        size_hint_y: None
        height: 120
        smooth_scroll_end: 10
        bar_width: '10dp'
        scroll_type: ['bars', 'content']
        
        BoxLayout:
            id: content_layout
            orientation: 'horizontal'
            size_hint_x: None
            size: self.minimum_width, dp(80)
            spacing: 10

    NestedScrollViewManager:
        ScrollView:
            id: outer_scroll
            do_scroll_x: False
            do_scroll_y: True
            smooth_scroll_end: 10
            bar_width: '10dp'
            scroll_type: ['bars', 'content']
            
            BoxLayout:
                id: outer_layout
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 20
    """

    class HorizontalScrollRow(ScrollView):
        row_number = NumericProperty(0)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            for i in range(10):
                btn = Button(
                    text=f'Button {self.row_number}-{i}',
                    size_hint_x=None,
                    width='100dp'
                )
                self.ids.content_layout.add_widget(btn)


    class NestedScrollKVApp(App):
        def build(self):
            return Builder.load_string(KV)
            
        def on_start(self):
            # Dynamically create 5 horizontal ScrollViews with buttons
            for i in range(10):
                # Create a horizontal ScrollView using the KV rule
                h_scroll = HorizontalScrollRow(row_number=i)
                # Get the content layout
                self.root.ids.outer_layout.add_widget(h_scroll)
            

    if __name__ == '__main__':
        NestedScrollKVApp().run()


Properties
----------

.. attribute:: parallel_delegation

    Controls boundary delegation behavior for parallel nested ScrollViews.
    
    When True (default, web-style):
        - Touch starting at inner boundary, moving away from boundary → 
          delegates to outer ScrollView
        - Touch starting not at boundary → scrolls inner only, never delegates
    
    When False:
        - No delegation, only touched ScrollView scrolls
        - Inner ScrollView shows overscroll effects at boundaries
        - Touch stays with initially touched ScrollView for entire gesture
    
    :attr:`parallel_delegation` is a :class:`~kivy.properties.BooleanProperty` 
    and defaults to True.

'''

# TODO: create a test suite for the updated ScrollView & NSVM for the kivy test suite.
# TODO: Register the NestedScrollViewManager with kv.
# TODO: deprecate dispatch_children() and dispatch_generic in _event.pyx
# TODO: formatting prior to PR

# TODO: Requested Feature: dwelling on a non-button widget can be turned into a scroll.

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty
from updated_sv import ScrollView


class NestedScrollViewManager(RelativeLayout):
    '''Touch routing coordinator for nested ScrollViews.
    
    See module documentation for detailed usage examples and behavior descriptions.
    
    .. versionadded:: 3.0.0
    '''

    parallel_delegation = BooleanProperty(True)
    '''Controls boundary delegation behavior for parallel nested ScrollViews.
    
    When True (default, web-style):
        - Touch starting at inner boundary, moving away → delegates to outer
        - Touch starting not at boundary → scrolls inner only, never delegates
    
    When False:
        - No delegation, only touched ScrollView scrolls
    
    :attr:`parallel_delegation` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to True.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer_scrollview = None
        self.inner_scrollview = None
        self._current_touch = None
    
    def _with_transform(self, touch, scrollview, callback):
        # Execute a callback with touch transformed to scrollview's coordinate space.
        
        # Args:
        #     touch: The touch event to transform
        #     scrollview: The ScrollView whose coordinate space to transform to
        #     callback: Function to call with transformed touch
            
        # Returns:
        #     The result of the callback
        touch.push()
        touch.apply_transform_2d(scrollview.parent.to_widget)
        try:
            result = callback(touch)
        finally:
            touch.pop()
        return result
    
    def _delegate_to_scrollview_children(self, touch, scrollview, method_name='on_touch_move'):
        # Delegate touch event to ScrollView's children in correct coordinate space.
        
        # Args:
        #     touch: The touch event
        #     scrollview: The ScrollView whose children to delegate to
        #     method_name: The method name to call (default: 'on_touch_move')
        
        # Returns:
        #     Result from _delegate_to_children
        return self._with_transform(
            touch, scrollview,
            lambda t: scrollview._delegate_to_children(t, method_name)
        )

    def _find_colliding_inner_scrollview(self, touch):
        # Find the first ScrollView that collides with the touch position.
        #
        # Args:
        #     touch: The touch event
        #
        # Returns:
        #     The first ScrollView that collides with the touch position
        
        viewport = self.outer_scrollview._viewport
        
        # Validate that viewport contains children (is a Layout)
        if not hasattr(viewport, 'children'):
            raise TypeError(
                f"NestedScrollViewManager: The outer ScrollView's viewport must be a Layout widget "
                f"to support nested scrolling. Got {type(viewport).__name__} which has no 'children' attribute. "
                f"Use BoxLayout, GridLayout, FloatLayout, or similar container widgets."
            )
        
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
            'nested_manager': self,
            'mode': None,  # 'inner' or 'outer'
            'delegation_mode': 'unknown'  # Will be set in ScrollView.on_scroll_start
        }
        
        # Classify nested configuration for mixed case handling
        if inner_scrollview:
            outer_axes = (outer_scrollview.do_scroll_x, outer_scrollview.do_scroll_y)
            inner_axes = (inner_scrollview.do_scroll_x, inner_scrollview.do_scroll_y)
            
            # Classify configuration
            is_orthogonal = (outer_axes[0] != inner_axes[0] and outer_axes[1] != inner_axes[1] 
                             and (outer_axes[0] or outer_axes[1]) and (inner_axes[0] or inner_axes[1]))
            is_parallel = (outer_axes == inner_axes)
            is_mixed = not is_orthogonal and not is_parallel
            
            if is_mixed:
                # Determine axis capabilities for mixed configurations
                shared = []
                outer_exclusive = []
                inner_exclusive = []
                
                # Check X axis
                if outer_axes[0] and inner_axes[0]:
                    shared.append('x')
                elif outer_axes[0] and not inner_axes[0]:
                    outer_exclusive.append('x')
                elif not outer_axes[0] and inner_axes[0]:
                    inner_exclusive.append('x')
                
                # Check Y axis
                if outer_axes[1] and inner_axes[1]:
                    shared.append('y')
                elif outer_axes[1] and not inner_axes[1]:
                    outer_exclusive.append('y')
                elif not outer_axes[1] and inner_axes[1]:
                    inner_exclusive.append('y')
                
                # Store compact axis configuration
                touch.ud['nsvm']['axis_config'] = {
                    'shared': shared,
                    'outer_exclusive': outer_exclusive,
                    'inner_exclusive': inner_exclusive
        }

        touch.push()
        touch.apply_transform_2d(outer_scrollview.parent.to_widget)
        in_bar_x, in_bar_y = outer_scrollview._check_scroll_bounds(touch)
        wheel_scroll = 'button' in touch.profile and touch.button.startswith('scroll')
        in_bar = in_bar_x or in_bar_y

        # MOUSE WHEEL SPECIAL HANDLING:
        if wheel_scroll:
            if inner_scrollview:
                # Determine scroll direction from button
                is_horizontal_wheel = touch.button in ('scrollleft', 'scrollright')
                is_vertical_wheel = touch.button in ('scrollup', 'scrolldown')
                
                # Mixed case logic:
                # - Shared axis → parallel rules (collision-based)
                # - Outer-only axis → always outer
                # - Inner-only axis → always inner
                
                target_scrollview = None
                use_parallel_rules = False
                
                if is_parallel:
                    # Pure parallel case: use collision-based routing for all wheel directions
                    use_parallel_rules = True
                else:
                    # Mixed case: determine routing based on wheel direction and axis capabilities
                    outer_x, outer_y = outer_axes
                    inner_x, inner_y = inner_axes
                    
                    if is_horizontal_wheel:
                        # Horizontal wheel scrolling
                        if outer_x and inner_x:
                            # Both can scroll X → parallel rules
                            use_parallel_rules = True
                        elif outer_x and not inner_x:
                            # Only outer scrolls X → always outer
                            target_scrollview = outer_scrollview
                        elif not outer_x and inner_x:
                            # Only inner scrolls X → always inner
                            target_scrollview = inner_scrollview
                    
                    elif is_vertical_wheel:
                        # Vertical wheel scrolling
                        if outer_y and inner_y:
                            # Both can scroll Y → parallel rules
                            use_parallel_rules = True
                        elif outer_y and not inner_y:
                            # Only outer scrolls Y → always outer
                            target_scrollview = outer_scrollview
                        elif not outer_y and inner_y:
                            # Only inner scrolls Y → always inner
                            target_scrollview = inner_scrollview
                
                # Apply routing decision
                if use_parallel_rules:
                    # Collision-based: check which scrollview the mouse is over
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

                elif target_scrollview:
                    # Direct routing to specific scrollview
                    touch.pop()
                    touch.push()
                    touch.apply_transform_2d(target_scrollview.parent.to_widget)
                    if target_scrollview._scroll_initialize(touch):
                        mode = 'inner' if target_scrollview == inner_scrollview else 'outer'
                        touch.pop()
                        touch.grab(self)
                        touch.ud['nsvm']['mode'] = mode
                        self._current_touch = touch
                        return True
                    touch.pop()
                    return False

            # For orthogonal scrollviews or no inner scrollview, outer scrollview handles the wheel
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
        
        # Check for claimed_by_child flag from either inner or outer scrollview
        # This flag is set by ScrollView._change_touch_mode when the scroll timeout
        # expires without reaching scroll_distance threshold, indicating the touch
        # should be handled by a child widget (e.g., Button, Slider) instead of scrolling.
        inner_uid = inner_scrollview._get_uid('claimed_by_child') if inner_scrollview else None
        outer_uid = outer_scrollview._get_uid('claimed_by_child') if outer_scrollview else None
        
        if (inner_uid and inner_uid in touch.ud) or (outer_uid and outer_uid in touch.ud):
            # Child widget (button, etc.) has claimed this touch - delegate to it
            mode = touch.ud['nsvm']['mode']
            scrollview = outer_scrollview if mode == 'outer' else inner_scrollview
            return self._delegate_to_scrollview_children(touch, scrollview)
        
        mode = touch.ud['nsvm']['mode']

        if not any(isinstance(key, str) and key.startswith('sv.')
                   for key in touch.ud):
            # Handle dragged widgets - pass to children to prevent crashes
            if mode == 'outer':
                return self._delegate_to_scrollview_children(touch, outer_scrollview)
            elif mode == 'inner':
                return self._delegate_to_scrollview_children(touch, inner_scrollview)
            else:
                raise ValueError(f"Invalid mode: {mode}")

        # Initialize scroll handling state
        touch.ud['sv.handled'] = {'x': False, 'y': False}
        # Track which axes have been handled by ScrollView to prevent
        # double-processing and coordinate multi-axis scrolling

        if mode == 'inner':
            # Call inner ScrollView's scroll update in its coordinate space
            result = self._with_transform(
                touch, self.inner_scrollview,
                lambda t: self.inner_scrollview._scroll_update(t)
            )

            # If inner ScrollView rejected the touch (orthogonal movement), delegate to outer
            if not result:
                # Transform touch to outer ScrollView's parent's coordinate space
                touch.push()
                touch.apply_transform_2d(self.outer_scrollview.parent.to_widget)

                # Ensure outer ScrollView effects are initialized for scrolling
                outer_uid = self.outer_scrollview._get_uid()
                if outer_uid not in touch.ud:
                    # CRITICAL: Create touch.ud[uid] entry for outer scrollview
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
                    self.outer_scrollview._touch = touch
                    touch.grab(self.outer_scrollview)
                    touch.ud['nsvm']['mode'] = 'outer'
                    
                    # Dispatch on_scroll_start for outer scrollview (delegation)
                    self.outer_scrollview.dispatch('on_scroll_start')
                    if self.inner_scrollview:
                        self.inner_scrollview._touch = None

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

                # CRITICAL: Always return True when delegating from inner to outer
                # This prevents the touch from being re-dispatched to child widgets (buttons).
                # Context: When we delegate mid-gesture from inner to outer scrollview, the touch
                # is already committed to scrolling. Returning False here would allow the touch
                # to propagate to child widgets, causing unwanted button presses during scroll.
                # Even if outer_result is False (e.g., at scroll boundary), we've taken ownership
                # of this touch for scrolling, so we must return True to consume it.
                return True
            return result

        elif mode == 'outer':
            # Call outer ScrollView's scroll update in its coordinate space
            return self._with_transform(
                touch, self.outer_scrollview,
                lambda t: self.outer_scrollview._scroll_update(t)
            )
        # This should never be reached - mode must be 'inner' or 'outer'
        raise ValueError(f"Invalid mode in on_touch_move: {mode}")

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
                raise ValueError(f"Invalid mode in on_touch_up: {mode}")
            
            # Delete uid from touch.ud to prevent double-processing
            # We've already called _scroll_finalize above, so scrollview's on_touch_up shouldn't process it again
            if mode == 'inner' and self.inner_scrollview:
                uid = self.inner_scrollview._get_uid()
                if uid in touch.ud:
                    del touch.ud[uid]
            elif mode == 'outer' and self.outer_scrollview:
                uid = self.outer_scrollview._get_uid()
                if uid in touch.ud:
                    del touch.ud[uid]

        # Always delegate to children after cleanup
            # This ensures buttons/widgets get their on_touch_up even if gesture became a scroll
        # Critical for preventing stuck button states and for touches not managed by this manager
        return super().on_touch_up(touch)


if __name__ == '__main__':
    from demo_nested_orthogonal import NestedScrollViewDemo

    NestedScrollViewDemo().run()
