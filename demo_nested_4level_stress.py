"""
4-Level Stress Test Demo (V->H->V->H)
===================================
Tests arbitrary depth nesting with 4 levels - maximum complexity test.

Structure:
- Level 1 (Outer): Vertical - Blue bars
  - Level 2: Horizontal - Green bars
    - Level 3: Vertical - Orange bars
      - Level 4 (Inner): Horizontal - Red bars
        - Content buttons

Expected Behavior:
1. All 4 levels scroll independently
2. Delegation cascades through all levels properly
3. V->H->V->H orthogonal delegation works
4. No performance issues with deep nesting
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from scrollview import ScrollView


class FourLevelStressDemo(App):
    def build(self):
        # Root container
        root = BoxLayout(orientation='vertical', padding=10)
        
        # Title
        title = Label(
            text='4-Level Stress Test (V->H->V->H)\n'
                 'Maximum nesting depth - tests delegation chain',
            size_hint_y=None,
            height=dp(60),
            color=[1, 1, 1, 1],
            bold=True
        )
        root.add_widget(title)
        
        # LEVEL 1: Outer (Vertical - Blue)
        level1_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(14),
            bar_color=[0.2, 0.4, 1.0, 0.9],  # Blue
            smooth_scroll_end=10
        )
        
        level1_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        level1_container.bind(minimum_height=level1_container.setter('height'))
        
        # Level 1 content before level 2
        for i in range(2):
            btn = Button(
                text=f'L1 Top {i+1} (V)',
                size_hint_y=None,
                height=dp(70),
                background_color=[0.2, 0.4, 1.0, 1]
            )
            level1_container.add_widget(btn)
        
        # LEVEL 2: Horizontal - Green
        level2_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            bar_width=dp(12),
            bar_color=[0.2, 1.0, 0.4, 0.9],  # Green
            size_hint_y=None,
            height=dp(500),
            smooth_scroll_end=10
        )
        
        level2_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_x=None,
            padding=dp(5)
        )
        level2_container.bind(minimum_width=level2_container.setter('width'))
        
        # Level 2 content before level 3
        for i in range(2):
            btn = Button(
                text=f'L2\nLeft\n{i+1}\n(H)',
                size_hint_x=None,
                width=dp(100),
                background_color=[0.2, 1.0, 0.4, 1]
            )
            level2_container.add_widget(btn)
        
        # LEVEL 3: Vertical - Orange
        level3_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(10),
            bar_color=[1.0, 0.6, 0.2, 0.9],  # Orange
            size_hint_x=None,
            width=dp(320),
            smooth_scroll_end=10
        )
        
        level3_container = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(5)
        )
        level3_container.bind(minimum_height=level3_container.setter('height'))
        
        # Level 3 content before level 4
        for i in range(2):
            btn = Button(
                text=f'L3 Top {i+1} (V)',
                size_hint_y=None,
                height=dp(60),
                background_color=[1.0, 0.6, 0.2, 1]
            )
            level3_container.add_widget(btn)
        
        # LEVEL 4: Innermost (Horizontal - Red)
        level4_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[1.0, 0.2, 0.2, 0.9],  # Red
            size_hint_y=None,
            height=dp(180),
            smooth_scroll_end=10
        )
        
        level4_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(6),
            size_hint_x=None,
            padding=dp(5)
        )
        level4_container.bind(minimum_width=level4_container.setter('width'))
        
        # Level 4 content (innermost)
        for i in range(25):
            btn = Button(
                text=f'L4\n{i+1}\n(H)',
                size_hint_x=None,
                width=dp(80),
                background_color=[1.0, 0.2, 0.2, 1]
            )
            level4_container.add_widget(btn)
        
        # Assemble hierarchy (innermost to outermost)
        level4_sv.add_widget(level4_container)
        level3_container.add_widget(level4_sv)
        
        # Level 3 content after level 4
        for i in range(2):
            btn = Button(
                text=f'L3 Bottom {i+1} (V)',
                size_hint_y=None,
                height=dp(60),
                background_color=[1.0, 0.6, 0.2, 1]
            )
            level3_container.add_widget(btn)
        
        level3_sv.add_widget(level3_container)
        level2_container.add_widget(level3_sv)
        
        # Level 2 content after level 3
        for i in range(2):
            btn = Button(
                text=f'L2\nRight\n{i+1}\n(H)',
                size_hint_x=None,
                width=dp(100),
                background_color=[0.2, 1.0, 0.4, 1]
            )
            level2_container.add_widget(btn)
        
        level2_sv.add_widget(level2_container)
        level1_container.add_widget(level2_sv)
        
        # Level 1 content after level 2
        for i in range(2):
            btn = Button(
                text=f'L1 Bottom {i+1} (V)',
                size_hint_y=None,
                height=dp(70),
                background_color=[0.2, 0.4, 1.0, 1]
            )
            level1_container.add_widget(btn)
        
        level1_sv.add_widget(level1_container)
        root.add_widget(level1_sv)
        
        # Instructions
        instructions = Label(
            text='Blue=L1(V), Green=L2(H), Orange=L3(V), Red=L4(H)\n'
                 'Scroll innermost first, watch cascade through 4 levels!',
            size_hint_y=None,
            height=dp(50),
            color=[0.8, 0.8, 0.8, 1]
        )
        root.add_widget(instructions)
        
        return root


if __name__ == '__main__':
    FourLevelStressDemo().run()

