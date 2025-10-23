"""
3-Level Orthogonal Nesting Demo (V->H->V)
========================================
Tests arbitrary depth nesting with alternating scroll directions.

Structure:
- Outer ScrollView (Vertical) - Blue bars
  - Middle ScrollView (Horizontal) - Green bars
    - Inner ScrollView (Vertical) - Red bars
      - Content buttons

Expected Behavior:
1. Vertical scroll on inner -> scrolls inner (red)
2. Horizontal scroll on inner -> delegates to middle (green)
3. Vertical scroll on middle -> delegates to outer (blue)
4. Each level only handles its designated direction
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from scrollview import ScrollView


class ThreeLevelOrthogonalDemo(App):
    def build(self):
        # Root container
        root = BoxLayout(orientation='vertical', padding=10)
        
        # Title
        title = Label(
            text='3-Level Orthogonal (V->H->V)\n'
                 'Drag vertically on innermost, then horizontally, then vertically on outer',
            size_hint_y=None,
            height=dp(60),
            color=[1, 1, 1, 1],
            bold=True
        )
        root.add_widget(title)
        
        # OUTER ScrollView (Vertical - Blue)
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(12),
            bar_color=[0.3, 0.5, 1.0, 0.9],  # Blue
            smooth_scroll_end=10
        )
        
        outer_container = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        outer_container.bind(minimum_height=outer_container.setter('height'))
        
        # Add outer content before middle
        for i in range(2):
            btn = Button(
                text=f'Outer Top (Vertical) {i+1}',
                size_hint_y=None,
                height=dp(80),
                background_color=[0.3, 0.5, 1.0, 1]  # Blue
            )
            outer_container.add_widget(btn)
        
        # MIDDLE ScrollView (Horizontal - Green)
        middle_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            bar_width=dp(10),
            bar_color=[0.3, 1.0, 0.5, 0.9],  # Green
            size_hint_y=None,
            height=dp(450),
            smooth_scroll_end=10
        )
        
        middle_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            size_hint_x=None,
            padding=dp(10)
        )
        middle_container.bind(minimum_width=middle_container.setter('width'))
        
        # Add middle content before inner
        for i in range(2):
            btn = Button(
                text=f'Middle\nLeft\n(Horiz)\n{i+1}',
                size_hint_x=None,
                width=dp(120),
                background_color=[0.3, 1.0, 0.5, 1]  # Green
            )
            middle_container.add_widget(btn)
        
        # INNER ScrollView (Vertical - Red)
        inner_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[1.0, 0.3, 0.3, 0.9],  # Red
            size_hint_x=None,
            width=dp(250),
            smooth_scroll_end=10
        )
        
        inner_container = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(10)
        )
        inner_container.bind(minimum_height=inner_container.setter('height'))
        
        # Add inner content
        for i in range(25):
            btn = Button(
                text=f'Inner {i+1}\n(Vertical)',
                size_hint_y=None,
                height=dp(60),
                background_color=[1.0, 0.3, 0.3, 1]  # Red
            )
            inner_container.add_widget(btn)
        
        inner_sv.add_widget(inner_container)
        middle_container.add_widget(inner_sv)
        
        # Add middle content after inner
        for i in range(2):
            btn = Button(
                text=f'Middle\nRight\n(Horiz)\n{i+1}',
                size_hint_x=None,
                width=dp(120),
                background_color=[0.3, 1.0, 0.5, 1]  # Green
            )
            middle_container.add_widget(btn)
        
        middle_sv.add_widget(middle_container)
        outer_container.add_widget(middle_sv)
        
        # Add outer content after middle
        for i in range(2):
            btn = Button(
                text=f'Outer Bottom (Vertical) {i+1}',
                size_hint_y=None,
                height=dp(80),
                background_color=[0.3, 0.5, 1.0, 1]  # Blue
            )
            outer_container.add_widget(btn)
        
        outer_sv.add_widget(outer_container)
        root.add_widget(outer_sv)
        
        # Instructions
        instructions = Label(
            text='Blue=Outer(V), Green=Middle(H), Red=Inner(V)\n'
                 'Try: V-scroll inner -> H-scroll delegates to middle -> V-scroll delegates to outer',
            size_hint_y=None,
            height=dp(50),
            color=[0.8, 0.8, 0.8, 1]
        )
        root.add_widget(instructions)
        
        return root


if __name__ == '__main__':
    ThreeLevelOrthogonalDemo().run()

