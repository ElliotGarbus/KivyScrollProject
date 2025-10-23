"""
3-Level Mixed Configuration Demo (XY->V->H)
==========================================
Tests arbitrary depth nesting with mixed scroll configurations.

Structure:
- Outer ScrollView (X+Y Both) - Blue bars
  - Middle ScrollView (Vertical only) - Green bars
    - Inner ScrollView (Horizontal only) - Red bars
      - Content buttons

Expected Behavior:
1. Horizontal scroll on inner -> scrolls inner (red)
2. Vertical scroll on inner -> delegates to middle (green) - inner can't handle vertical
3. Middle scrolls vertically
4. Horizontal scroll on middle -> delegates to outer (blue) - middle can't handle horizontal
5. Outer scrolls in both directions
Note: Middle hitting vertical boundary currently doesn't delegate to outer (same as V->H->V).
See Phase 8 for planned enhancement.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from scrollview import ScrollView


class ThreeLevelMixedDemo(App):
    def build(self):
        # Root container
        root = BoxLayout(orientation='vertical', padding=10)
        
        # Title
        title = Label(
            text='3-Level Mixed (XY->V->H)\n'
                 'Outer scrolls both, Middle vertical only, Inner horizontal only',
            size_hint_y=None,
            height=dp(60),
            color=[1, 1, 1, 1],
            bold=True
        )
        root.add_widget(title)
        
        # OUTER ScrollView (Both X and Y - Blue)
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(12),
            bar_color=[0.3, 0.5, 1.0, 0.9],  # Blue
            smooth_scroll_end=10
        )
        
        # Use GridLayout for outer to support both directions
        outer_container = GridLayout(
            cols=1,
            spacing=dp(15),
            size_hint=(None, None),
            padding=dp(10)
        )
        outer_container.bind(
            minimum_height=outer_container.setter('height'),
            minimum_width=outer_container.setter('width')
        )
        
        # Add outer content before middle
        for i in range(2):
            row = BoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint=(None, None),
                height=dp(80)
            )
            row.bind(minimum_width=row.setter('width'))
            for j in range(5):
                btn = Button(
                    text=f'Outer\nTop\n{i+1},{j+1}',
                    size_hint=(None, None),
                    size=(dp(120), dp(80)),
                    background_color=[0.3, 0.5, 1.0, 1]  # Blue
                )
                row.add_widget(btn)
            outer_container.add_widget(row)
        
        # MIDDLE ScrollView (Vertical only - Green)
        middle_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(10),
            bar_color=[0.3, 1.0, 0.5, 0.9],  # Green
            size_hint=(None, None),
            size=(dp(600), dp(400)),
            smooth_scroll_end=10
        )
        
        middle_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        middle_container.bind(minimum_height=middle_container.setter('height'))
        
        # Add middle content before inner
        for i in range(2):
            btn = Button(
                text=f'Middle Top (Vertical) {i+1}',
                size_hint_y=None,
                height=dp(70),
                background_color=[0.3, 1.0, 0.5, 1]  # Green
            )
            middle_container.add_widget(btn)
        
        # INNER ScrollView (Horizontal only - Red)
        inner_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[1.0, 0.3, 0.3, 0.9],  # Red
            size_hint_y=None,
            height=dp(200),
            smooth_scroll_end=10
        )
        
        inner_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_x=None,
            padding=dp(10)
        )
        inner_container.bind(minimum_width=inner_container.setter('width'))
        
        # Add inner content
        for i in range(20):
            btn = Button(
                text=f'Inner\n{i+1}\n(Horiz)',
                size_hint_x=None,
                width=dp(100),
                background_color=[1.0, 0.3, 0.3, 1]  # Red
            )
            inner_container.add_widget(btn)
        
        inner_sv.add_widget(inner_container)
        middle_container.add_widget(inner_sv)
        
        # Add middle content after inner
        for i in range(2):
            btn = Button(
                text=f'Middle Bottom (Vertical) {i+1}',
                size_hint_y=None,
                height=dp(70),
                background_color=[0.3, 1.0, 0.5, 1]  # Green
            )
            middle_container.add_widget(btn)
        
        middle_sv.add_widget(middle_container)
        outer_container.add_widget(middle_sv)
        
        # Add outer content after middle
        for i in range(2):
            row = BoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint=(None, None),
                height=dp(80)
            )
            row.bind(minimum_width=row.setter('width'))
            for j in range(5):
                btn = Button(
                    text=f'Outer\nBot\n{i+1},{j+1}',
                    size_hint=(None, None),
                    size=(dp(120), dp(80)),
                    background_color=[0.3, 0.5, 1.0, 1]  # Blue
                )
                row.add_widget(btn)
            outer_container.add_widget(row)
        
        outer_sv.add_widget(outer_container)
        root.add_widget(outer_sv)
        
        # Instructions
        instructions = Label(
            text='Blue=Outer(XY), Green=Middle(V), Red=Inner(H)\n'
                 'H-scroll inner -> inner handles | V-scroll inner -> middle | H-scroll middle -> outer',
            size_hint_y=None,
            height=dp(50),
            color=[0.8, 0.8, 0.8, 1]
        )
        root.add_widget(instructions)
        
        return root


if __name__ == '__main__':
    ThreeLevelMixedDemo().run()

