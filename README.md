Proposed implementation for nested scrollviews. They will be under a NestedScrollViewManager. It will look something like this:

```
NestedScrollViewManager:
    ScrollView:  # the outer scrollview
        ...attributes and layout
        ...
        ...ScrollView:  # one or more scrollviews deeper in the widget tree
```
My objective is to deliver a solution that is more maintainable both for ScrollView and the NestedScrollViewManager.

The Nested ScrollView manager supports two levels of nesting.  An outer ScrollView and one or more inner ScrollViews.  
All combinations for do_scroll_x and do_scroll_y are supported for the inner and outer ScrollView.

The on_scroll_events (on_scroll_start, on_scroll_move, and on_stroll_stop) have been updated.  They now work as expected, firing when the movement starts, continues and stops.  

**ScrollView has a new property, slow_device_support**

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

**The NestedScrollViewManger has one property, parallel_delegation**

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




Key files:
 - nested_scrollview_manager.py - The NestedScrollViewManager
 - updated_sv.py - ScrollView simplified and adapted to work with the NestedScrollViewManager

Demonstrations/tests using the updated scrollview and the NestedScrollManager:
- demo_nested_orthogonal.py - Nested orthogonal ScrollViews (vertical outer, horizontal inner) using the NestedScrollViewManager
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

- demo_scroll_events_non_neseted.py - tool for observing scroll event firing (start, move, stop) within a single, non-nested ScrollView
- demo_scroll_events_nested.py - color-coded scroll events for nested vertical and horizontal ScrollViews; in nested scenarios.

- demo_drag_over_scroll.py - Dragging a button over a single ScrollView
- demo_drag_from_scroll.py - Dragging buttons out of a single ScrollView
- demo_drag_nested_scroll.py - Dragging buttons out of nested orthogonal ScrollViews 

Other Files:
- og_nested_verticals.py - demonstrates the kivy v2.31 nesting.  Only parallel nesting is supported, has artifacts.
- my_scrollview.py - attempt to support nesting with minor modificaitons to the original ScrollView. (Abandoned)


 The NestedScrollViewManger is not registered.  Register if you want to use with kv.
