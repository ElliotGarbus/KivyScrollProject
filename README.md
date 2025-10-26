Updated implementation for ScrollView with full nesting support.  Supports nesting to arbitrary levels.

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
    
    



Key files:
Directory "V0 Obsolete" was an initial implementation that uses a NestedScrollViewManger to route the touches 
to the inner and outer ScrollView. Things worked nicely, but I have decided to integrate the capabilities back into
ScrollView, rather than have two separate widgets.

Directory V1 Two Level Nesting - this version of ScrollView supports two levels of nesting, outer and inner. Obsolte. 

In the main directory I am working to support arbitary levels of nesting scrollview.

 - scrollview.py - ScrollView with Nesting support

Demonstrations/tests using the updated ScrollView: 
- demo_monster_nesting.py - 12 nesting configurations in an xy scroll view.
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

