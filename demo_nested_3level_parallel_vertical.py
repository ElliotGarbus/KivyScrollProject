"""
3-Level Parallel Vertical Nesting Demo (V->V->V)
==============================================
Tests arbitrary depth nesting with 3 levels of vertically scrolling ScrollViews.

Structure:
- Outer ScrollView (Vertical) - Blue bars
  - Middle ScrollView (Vertical) - Green bars  
    - Inner ScrollView (Vertical) - Red bars
      - Content buttons

Expected Behavior:
1. Touch innermost buttons - inner scrolls
2. Scroll inner to boundary - middle takes over
3. Scroll middle to boundary - outer takes over
4. All 3 levels scroll independently in sequence
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from scrollview import ScrollView


class ThreeLevelParallelDemo(App):
    def build(self):
        # Root container
        root = BoxLayout(orientation='vertical', padding=10)
        
        # Title
        title = Label(
            text='3-Level Parallel Vertical (V->V->V)\n'
                 'Scroll the innermost, then middle, then outer',
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
            smooth_scroll_end=10,
            parallel_delegation=True  # Enable boundary delegation
        )
        
        outer_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        outer_container.bind(minimum_height=outer_container.setter('height'))
        
        # Add outer content before middle
        for i in range(3):
            btn = Button(
                text=f'Outer Top Button {i+1}',
                size_hint_y=None,
                height=dp(80),
                background_color=[0.3, 0.5, 1.0, 1]  # Blue
            )
            outer_container.add_widget(btn)
        
        # MIDDLE ScrollView (Vertical - Green)
        middle_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(10),
            bar_color=[0.3, 1.0, 0.5, 0.9],  # Green
            size_hint_y=None,
            height=dp(500),
            smooth_scroll_end=10,
            parallel_delegation=True  # Enable boundary delegation
        )
        
        middle_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        middle_container.bind(minimum_height=middle_container.setter('height'))
        
        # Add middle content before inner
        for i in range(3):
            btn = Button(
                text=f'Middle Top Button {i+1}',
                size_hint_y=None,
                height=dp(70),
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
            size_hint_y=None,
            height=dp(300),
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
        for i in range(20):
            btn = Button(
                text=f'Inner Button {i+1}\n(Scroll me first!)',
                size_hint_y=None,
                height=dp(60),
                background_color=[1.0, 0.3, 0.3, 1]  # Red
            )
            inner_container.add_widget(btn)
        
        inner_sv.add_widget(inner_container)
        middle_container.add_widget(inner_sv)
        
        # Add middle content after inner
        for i in range(3):
            btn = Button(
                text=f'Middle Bottom Button {i+1}',
                size_hint_y=None,
                height=dp(70),
                background_color=[0.3, 1.0, 0.5, 1]  # Green
            )
            middle_container.add_widget(btn)
        
        middle_sv.add_widget(middle_container)
        outer_container.add_widget(middle_sv)
        
        # Add outer content after middle
        for i in range(3):
            btn = Button(
                text=f'Outer Bottom Button {i+1}',
                size_hint_y=None,
                height=dp(80),
                background_color=[0.3, 0.5, 1.0, 1]  # Blue
            )
            outer_container.add_widget(btn)
        
        outer_sv.add_widget(outer_container)
        root.add_widget(outer_sv)
        
        # Instructions
        instructions = Label(
            text='Blue=Outer, Green=Middle, Red=Inner\n'
                 'Scroll inner to boundary -> cascades to middle -> cascades to outer',
            size_hint_y=None,
            height=dp(50),
            color=[0.8, 0.8, 0.8, 1]
        )
        root.add_widget(instructions)
        
        return root


if __name__ == '__main__':
    ThreeLevelParallelDemo().run()

