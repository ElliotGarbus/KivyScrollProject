Proposed implementation for nested scrollviews. They will be under a NestedScrollViewManager. It will look something like this:

```
NestedScrollViewManager:
    ScrollView:  # the outer scrollview
        ...attributes and layout
        ...
        ...ScrollView:  # one or more scrollviews deeper in the widget tree
```
My objective is to deliver a solution that is more maintainable both for ScrollView and the NestedScrollViewManager.

Key files:
 - nested_scrollview_manager.py - The NestedScrollViewManager
 - updated_sv.py - ScrollView simplified and adapted to work with the NestedScrollViewManager
 - demo_NSVM.py - a sample nested scrollview
