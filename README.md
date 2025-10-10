Proposed implementation for nested scrollviews. They will be under a NestedScrollViewManager. It will look something like this:

```
NestedScrollViewManager:
    ScrollView:  # the outer scrollview
        ...attributes and layout
        ...
        ...ScrollView:  # one or more scrollviews deeper in the widget tree
```
My objective is to deliver a solution that is more maintainable both for ScrollView and the NestedScrollViewManager.

The Nested ScrollView manager supports two levels of nesting.  An ourter scrollview and one or more inner scrollviews.  All combinaations for do_scroll_x and do_scroll_y are supported for the inner and outer scrollview.

The on_scroll_events (on_scroll_start, on_scroll_move, and on_stroll_stop) have been updated.  They now work as expected, firing when the movement starts, continues and stops.  




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

- demo_single_horizontal - non-nested horizontal scrollview
- demo_single_vertical - non-nested vertical scrollview
- demo_single_xy - non-nested XY scrollview

- demo_scroll_events_non_neseted.py - tool for observing scroll event firing (start, move, stop) within a single, non-nested ScrollView
- demo_scroll_events_nested.py - color-coded scroll events for nested vertical and horizontal ScrollViews; in nested scenarios. 

Other Files:
- og_nested_verticals.py - demonstrates the kivy v2.31 nesting.  Only parallel nesting is supported, has artifacts.
- my_scrollview.py - attempt to support nesting with minor modificaitons to the original ScrollView. (Abandond)


 The NestedScrollViewManger is not registered.  Register if you want to use with kv.
