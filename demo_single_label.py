"""
Simple ScrollView Demo - Single Label
======================================
Demonstrates the most basic ScrollView usage: a Label with long text content
that scrolls vertically.
"""

from kivy.app import App
from kivy.uix.label import Label
from scrollview import ScrollView


class SingleLabelDemo(App):
    def build(self):
        # Create a ScrollView (vertical scrolling only)
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width='10dp',
            bar_color=[0.3, 0.6, 1.0, 0.8]
        )
        
        # Create a Label with lots of text
        label = Label(
            text=self._get_sample_text(),
            size_hint_y=None,  # Don't use size hint for height
            padding=('20dp', '20dp'),
            markup=True,
            halign='left',
            valign='top',
            color=[1, 1, 1, 1]
        )
        
        # Bind texture_size to height so label grows with content
        label.bind(texture_size=label.setter('size'))
        # Bind width to text_size so text wraps
        label.bind(width=lambda *x: label.setter('text_size')(label, (label.width, None)))
        
        scroll.add_widget(label)
        return scroll
    
    def _get_sample_text(self):
        """Generate sample text content."""
        return """[b][size=24]ScrollView Documentation[/size][/b]

[b]Overview[/b]
The ScrollView widget provides a scrollable/pannable viewport that is clipped to the 
ScrollView's bounding box. It allows users to view content that is larger than the 
available display area by scrolling or panning.

[b]Basic Usage[/b]
ScrollView accepts only one child widget. If you need multiple widgets, wrap them in a 
layout (BoxLayout, GridLayout, etc.) and add that layout to the ScrollView.

The child widget should have either:
• size_hint_y=None and an explicit height for vertical scrolling
• size_hint_x=None and an explicit width for horizontal scrolling
• Both for scrolling in both directions

[b]Properties[/b]

[b]do_scroll_x[/b] / [b]do_scroll_y[/b]
Enable or disable scrolling on the X or Y axis. Set to False to prevent scrolling in 
that direction.

[b]scroll_type[/b]
Controls the scrolling interface:
• ['content'] - Scroll by dragging the content
• ['bars'] - Scroll by dragging scrollbars only
• ['bars', 'content'] - Both methods available (default)

[b]bar_width[/b]
Width of the scrollbars in pixels. Default is 2dp.

[b]bar_color[/b]
Color of the scrollbars in [R, G, B, A] format.

[b]scroll_distance[/b]
Minimum distance to travel before the touch is considered a scroll gesture. Default is 20dp.

[b]scroll_timeout[/b]
Timeout in milliseconds before the touch is considered a scroll gesture. Default is 55ms.

[b]Nested ScrollViews[/b]
This ScrollView implementation supports nesting ScrollViews at arbitrary depth with 
intelligent touch handling:

[b]Orthogonal Scrolling[/b]
When outer and inner ScrollViews scroll in different directions (e.g., vertical outer 
with horizontal inner), each handles touches in its scroll direction automatically.

[b]Parallel Scrolling[/b]
When ScrollViews scroll in the same direction, web-style boundary delegation is used:
• Touch at boundary moving outward → delegates to outer immediately
• Touch at boundary moving inward → scrolls inner only
• Touch not at boundary → scrolls inner only

[b]Mixed Scrolling[/b]
When combining XY and single-axis ScrollViews, shared axes use parallel rules while 
exclusive axes use orthogonal rules.

[b]Advanced Properties[/b]

[b]parallel_delegation[/b]
Controls boundary delegation for parallel nested ScrollViews. When True (default), 
uses web-style delegation. When False, only the touched ScrollView scrolls.

[b]delegate_to_outer[/b]
Controls whether gestures delegate to outer ScrollViews. When False, prevents any 
delegation upward in the hierarchy.

[b]slow_device_support[/b]
When enabled, adds a 3-frame delay for scroll detection on slow devices. Disabled by 
default for better responsiveness on modern hardware.

[b]smooth_scroll_end[/b]
Duration in frames for smooth deceleration at the end of scrolling. Higher values 
create smoother, longer deceleration.

[b]Events[/b]

[b]on_scroll_start[/b]
Fired when scrolling begins (after scroll_timeout and scroll_distance are satisfied).

[b]on_scroll_move[/b]
Fired continuously while scrolling is active.

[b]on_scroll_stop[/b]
Fired when scrolling ends and the ScrollView comes to rest.

[b]Performance Tips[/b]
• Use RecycleView for long lists instead of many widgets in a ScrollView
• Set size_hint to None on the scrolling axis
• Bind minimum_height/width to height/width for dynamic content
• Avoid complex widget trees inside ScrollViews when possible

[b]Common Patterns[/b]

Vertical list:
    ScrollView:
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height

Horizontal gallery:
    ScrollView:
        BoxLayout:
            orientation: 'horizontal'
            size_hint_x: None
            width: self.minimum_width

XY scrolling:
    ScrollView:
        do_scroll_x: True
        do_scroll_y: True
        FloatLayout:
            size_hint: None, None
            size: 2000, 2000

[b]Troubleshooting[/b]

[b]Content not scrolling?[/b]
• Check that size_hint is None on the scrolling axis
• Verify content size exceeds ScrollView size
• Ensure do_scroll_x/y is True for the desired axis

[b]Nested scrolling not working?[/b]
• Verify both ScrollViews have do_scroll_x/y set correctly
• Check if touches are being captured by intermediate widgets
• Review parallel_delegation and delegate_to_outer settings

[b]Buttons not clickable?[/b]
• Reduce scroll_timeout (default 55ms might be too long)
• Ensure scroll_distance is appropriate for your use case
• Check if widgets are grabbing touches unnecessarily

This is a simple demonstration of a single label in a ScrollView. Scroll up and down 
to view all the content!
"""


if __name__ == '__main__':
    SingleLabelDemo().run()

