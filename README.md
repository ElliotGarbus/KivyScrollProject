Updated implementation for ScrollView with full nesting support. Supports nesting to arbitrary levels.

The on_scroll_events (on_scroll_start, on_scroll_move, and on_stroll_stop) have been updated.
They now work as expected, firing when the movement starts, continues and stops.

**New ScrollView Properties**

slow_device_support = BooleanProperty(False)


    In 2014, an additional 3 frame delay was added to ScollView to detect
    the start of scrolling - the delay was added to support slow Android devices.  
    This is now an option that is False by default.
    
    On very slow devices, at least 3 frames are needed to accumulate
    velocity data for scroll effects to work properly. When enabled,
    after the scroll timeout expires, the gesture handoff will be delayed
    until at least 3 frames have rendered, ensuring sufficient velocity
    data accumulation.
    
    This addresses issues #1464 and #1499 for low-performance devices.
    
    The default value (False) is seleted for modern hardware 
    to improve touch responsiveness.  If there is an issue with ScrollDetection on 
    lower performance devices, set slow_device_support to True.

parallel_delegation = BooleanProperty(True)

    Controls boundary delegation for parallel nested ScrollViews.
    
    When True (default, web-style):
    - Touch starting at inner boundary, moving away from boundary → delegates to outer scrollview
    - else → scrolls inner only, never delegates
    
    When False:
    - No delegation, only touched scrollview scrolls
    - Inner scrollview shows overscroll effects at boundaries
    - Touch stays with initially touched scrollview for entire gesture
    
    Default: True (web-style)

delegate_to_outer = BooleanProperty(True)

    Controls whether scroll gestures delegate to outer ScrollViews.
    
    When True (default):
        - Orthogonal: Cross-axis gestures immediately delegate to outer
          (e.g., horizontal swipe in vertical-only ScrollView)
        - Parallel: At boundaries, delegates to outer (respects parallel_delegation)
        - Arbitrary depth: Continues searching up hierarchy for capable ScrollView
    
    When False:
        - No delegation to outer ScrollViews
        - Only the directly touched ScrollView handles the gesture
    
    Example use cases:
        - Set False to lock scrolling to a specific nested level
        - Set False to prevent inner scroll from affecting outer scroll

Nested Scrolling Behavior
-------------------------

The ScrollView automatically detects the scrolling configuration 
and applies appropriate behavior:

**Orthogonal Scrolling** (outer and inner scroll in different directions):
    - Touch scrolling: Each ScrollView handles touches in its scroll direction
    - Mouse wheel: Scrolls innermost ScrollView if it can handle the direction
    - Example: Vertical outer + Horizontal inner

**Parallel Scrolling** (outer and inner scroll in the same direction):
    - Touch scrolling: Uses web-style boundary delegation (see below)
    - Mouse wheel: Scrolls innermost ScrollView, no boundary delegation
    - Scrollbar: Does not propagate scroll to the other ScrollView
    - Example: Vertical outer + Vertical inner

**Mixed Scrolling** (outer scrolls XY, inner scrolls single axis, or vice versa):
    - Shared axis: Uses web-style boundary delegation
    - Exclusive axes: Immediate delegation or inner-only scrolling
    - Mouse wheel: Scrolls innermost ScrollView if it can handle the direction
    - Example: XY outer + Horizontal inner


Web-Style Boundary Delegation
------------------------------

For parallel and shared-axis scrolling, the ScrollView implements web-style 
delegation behavior:

    - Touch starts at inner boundary, moves away → delegates to outer immediately
    - Touch starts at inner boundary, moves inward → scrolls inner only
    - Touch starts not at boundary → scrolls inner only, never delegates 
      (even when reaching boundary mid-gesture)
    - New touch required at boundary to delegate to outer

This behavior can be disabled by setting :attr:`parallel_delegation` to False.


Wheel Behavior in Nested ScrollViews
--------------------------------------------

When using a mouse scroll wheel (or trackpad equivalent), the ScrollView applies
*web-style* delegation:

- **Wheel events are handled by only the innermost ScrollView under the
  pointer/cursor.**
- If that ScrollView cannot scroll further in the wheel's axis, the event is
  *not propagated* to outer ScrollViews. This matches standard browser and OS
  behaviors.
- Outer ScrollViews can only respond to the wheel if the pointer is over their
  scrollbars *or* if there are no nested ScrollViews at the pointer position.

This prevents "scroll hijacking," ensuring natural, intuitive nested scroll
experiences.

**Examples:**
- If you have a vertical ScrollView containing a horizontal ScrollView, and you
  use the mouse wheel over the inner (horizontal) ScrollView, only the vertical
  outer ScrollView scrolls (since the direction matches).
- With two nested vertical ScrollViews, the wheel will only scroll the
  innermost ScrollView under the pointer until it can scroll no further, at
  which point further scrolling does not delegate to the parent.

This behavior is always active for wheel events and is NOT affected by
the :attr:`parallel_delegation` or :attr:`delegate_to_outer` properties,
which only control touch/touchpad gesture behavior.
'''



Key files:

In the main directory:

 - scrollview.py - ScrollView with Nesting support

Demonstrations/tests using the updated ScrollView: 
- demo_delegation_monster.py - 12 nesting configurations in an xy scroll view, with outer delegation control.
- demo_nested_orthogonal.py - Nested orthogonal ScrollViews (vertical outer, horizontal inner) 
- demo_nested_horizontal.py - Horizontal parallel ScrollViews 
- demo_nested_vertical.py - Multiple vertical parallel ScrollViews
- demo_nested_xy.py - XY ScrollViews nested in an XY ScrollView
- demo_nested_xy_mixed.py - Demo showing XY outer with single-axis inner ScrollViews
- demo_nested_single_xy.py - Demo showing single-axis outer with XY inner ScrollViews

- demo_nested_slider.py - slider in an nested scrollview
- demo_single_slider.py - slider in a non-nested scrollview

- demo_single_horizontal - non-nested horizontal scrollview
- demo_single_vertical - non-nested vertical scrollview
- demo_single_xy - non-nested XY scrollview

- demo_scroll_events_non_neseted.py - observing scroll event firing (start, move, stop) within a single, non-nested ScrollView
- demo_scroll_events_nested.py - color-coded scroll events for nested vertical and horizontal ScrollViews; in nested scenarios.

- demo_drag_from_scroll.py - Dragging buttons out of a single ScrollView
- demo_drag_nested_scroll.py - Dragging buttons out of nested orthogonal ScrollViews 

Obsolete implmentations - how development progressed:
- Directory "V0 Obsolete" was an initial implementation that uses a NestedScrollViewManger to route the touches 
to the inner and outer ScrollView. Things worked nicely, but I have decided to integrate the capabilities back into
ScrollView, rather than have two separate widgets.

- Directory V1 Two Level Nesting - this version of ScrollView supports two levels of nesting, outer and inner.