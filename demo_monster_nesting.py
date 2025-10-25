"""
Monster Nesting Demo - Comprehensive ScrollView Test
=====================================================
Combines multiple nested ScrollView configurations into one large grid.
Each cell demonstrates a different nesting pattern:
- Parallel vertical (V->V)
- Parallel horizontal (H->H)
- Orthogonal (V->H, H->V)
- XY nested (XY->XY)
- Mixed (XY->H, XY->V)
- 3-level nesting (V->V->V, V->H->V)

This stress tests multiple complex nesting scenarios simultaneously.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from scrollview import ScrollView


class MonsterNestingDemo(App):
    """Main app with XY outer ScrollView containing a grid of different nested demos."""
    
    def build(self):
        # Outer XY ScrollView
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(12),
            bar_color=[1.0, 1.0, 0.0, 0.9],
            smooth_scroll_end=10
        )
        
        # Main container with padding
        main_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            padding=dp(20),
            spacing=dp(15)
        )
        main_container.bind(minimum_width=main_container.setter('width'))
        main_container.bind(minimum_height=main_container.setter('height'))
        
        # Title
        title = Label(
            text='Monster Nesting Demo - 12 Configurations',
            size_hint=(None, None),
            width=dp(1400),
            height=dp(50),
            color=[1, 1, 0, 1],
            bold=True,
            font_size='24sp',
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        main_container.add_widget(title)
        
        # Outer vertical BoxLayout containing 4 rows
        # Each row is a horizontal BoxLayout containing 3 panels
        
        # Row 0 - Basic single ScrollViews (for comparison)
        row0 = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint=(None, None),
            height=dp(450)
        )
        row0.bind(minimum_width=row0.setter('width'))
        row0.add_widget(self._create_single_vertical())
        row0.add_widget(self._create_single_horizontal())
        row0.add_widget(self._create_single_xy())
        main_container.add_widget(row0)
        
        # Row 1 - Parallel nesting
        row1 = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint=(None, None),
            height=dp(450)
        )
        row1.bind(minimum_width=row1.setter('width'))
        row1.add_widget(self._create_parallel_vertical())
        row1.add_widget(self._create_parallel_horizontal())
        row1.add_widget(self._create_orthogonal_v_h())
        main_container.add_widget(row1)
        
        # Row 2
        row2 = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint=(None, None),
            height=dp(450)
        )
        row2.bind(minimum_width=row2.setter('width'))
        row2.add_widget(self._create_orthogonal_h_v())
        row2.add_widget(self._create_xy_nested())
        row2.add_widget(self._create_mixed_xy_h())
        main_container.add_widget(row2)
        
        # Row 3
        row3 = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint=(None, None),
            height=dp(450)
        )
        row3.bind(minimum_width=row3.setter('width'))
        row3.add_widget(self._create_mixed_xy_v())
        row3.add_widget(self._create_3level_vertical())
        row3.add_widget(self._create_3level_orthogonal())
        main_container.add_widget(row3)
        outer_sv.add_widget(main_container)
        
        return outer_sv
    
    def _create_panel_container(self, title_text, color):
        """Create a standardized panel container with title."""
        container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=dp(420),
            height=dp(450),
            padding=dp(10),
            spacing=dp(5)
        )
        
        # Title label
        title = Label(
            text=title_text,
            size_hint_y=None,
            height=dp(40),
            color=color,
            bold=True,
            font_size='16sp',
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        container.add_widget(title)
        
        return container
    
    def _create_single_vertical(self):
        """Single Vertical ScrollView (V)"""
        panel = self._create_panel_container('Single Vertical\n(V)', [0.5, 0.5, 1.0, 1])
        
        # Single vertical ScrollView
        sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.5, 0.5, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        content = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Add buttons
        for i in range(20):
            btn = Button(
                text=f'V-{i+1}',
                size_hint_y=None,
                height=dp(45),
                background_color=[0.3, 0.3, 0.9, 1]
            )
            content.add_widget(btn)
        
        sv.add_widget(content)
        panel.add_widget(sv)
        return panel
    
    def _create_single_horizontal(self):
        """Single Horizontal ScrollView (H)"""
        panel = self._create_panel_container('Single Horizontal\n(H)', [1.0, 0.5, 0.5, 1])
        
        # Single horizontal ScrollView
        sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[1.0, 0.5, 0.5, 0.8],
            smooth_scroll_end=10
        )
        
        content = BoxLayout(
            orientation='horizontal',
            spacing=dp(5),
            size_hint_x=None,
            padding=dp(5)
        )
        content.bind(minimum_width=content.setter('width'))
        
        # Add buttons
        for i in range(15):
            btn = Button(
                text=f'H\n{i+1}',
                size_hint_x=None,
                width=dp(70),
                background_color=[0.9, 0.3, 0.3, 1]
            )
            content.add_widget(btn)
        
        sv.add_widget(content)
        panel.add_widget(sv)
        return panel
    
    def _create_single_xy(self):
        """Single XY ScrollView (XY)"""
        panel = self._create_panel_container('Single XY\n(XY)', [0.5, 1.0, 0.5, 1])
        
        # Single XY ScrollView
        sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.5, 1.0, 0.5, 0.8],
            smooth_scroll_end=10
        )
        
        content = GridLayout(
            cols=9,  # 9 columns for wider scrolling
            spacing=dp(5),
            size_hint=(None, None),
            padding=dp(5)
        )
        content.bind(minimum_width=content.setter('width'))
        content.bind(minimum_height=content.setter('height'))
        
        # Add buttons
        for i in range(99):  # 11 rows x 9 cols
            btn = Button(
                text=f'XY\n{i+1}',
                size_hint=(None, None),
                size=(dp(70), dp(50)),
                background_color=[0.3, 0.9, 0.3, 1]
            )
            content.add_widget(btn)
        
        sv.add_widget(content)
        panel.add_widget(sv)
        return panel
    
    def _create_parallel_vertical(self):
        """Parallel Vertical: V->V (both scroll vertically)"""
        panel = self._create_panel_container('Parallel Vertical\n(V->V)', [0.3, 0.8, 1.0, 1])
        
        # Outer vertical ScrollView - explicit size
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),  # Fixed viewport size
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Add 5 inner vertical ScrollViews (more than fits)
        for i in range(5):
            inner_sv = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint_y=None,
                height=dp(100),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8]
            )
            
            inner_content = GridLayout(
                cols=1,
                spacing=dp(5),
                size_hint_y=None,
                padding=dp(5)
            )
            inner_content.bind(minimum_height=inner_content.setter('height'))
            
            for j in range(10):
                btn = Button(
                    text=f'V{i+1}-{j+1}',
                    size_hint_y=None,
                    height=dp(40),
                    background_color=[0.2 + i*0.15, 0.3, 0.7, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_parallel_horizontal(self):
        """Parallel Horizontal: H->H (both scroll horizontally)"""
        panel = self._create_panel_container('Parallel Horizontal\n(H->H)', [0.3, 1.0, 0.8, 1])
        
        # Outer horizontal ScrollView - explicit size
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),  # Fixed viewport size
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.6, 0.8],
            smooth_scroll_end=10
        )
        
        outer_content = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_x=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_width=outer_content.setter('width'))
        
        # Add 4 inner horizontal ScrollViews (more than fits)
        for i in range(4):
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint_x=None,
                width=dp(120),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8]
            )
            
            inner_content = BoxLayout(
                orientation='horizontal',
                spacing=dp(5),
                size_hint_x=None,
                padding=dp(5)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            
            for j in range(8):
                btn = Button(
                    text=f'H{i+1}\n{j+1}',
                    size_hint_x=None,
                    width=dp(60),
                    background_color=[0.7, 0.3, 0.2 + i*0.15, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_orthogonal_v_h(self):
        """Orthogonal: V->H (outer vertical, inner horizontal)"""
        panel = self._create_panel_container('Orthogonal V->H', [1.0, 0.8, 0.3, 1])
        
        # Outer vertical ScrollView - explicit size
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),  # Fixed viewport size
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Add 5 inner horizontal ScrollViews (more than fits)
        for i in range(5):
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint_y=None,
                height=dp(100),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8]
            )
            
            inner_content = BoxLayout(
                orientation='horizontal',
                spacing=dp(5),
                size_hint_x=None,
                padding=dp(5)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            
            for j in range(10):
                btn = Button(
                    text=f'R{i+1}\n{j+1}',
                    size_hint_x=None,
                    width=dp(60),
                    background_color=[0.2 + i*0.12, 0.5, 0.8, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_orthogonal_h_v(self):
        """Orthogonal: H->V (outer horizontal, inner vertical)"""
        panel = self._create_panel_container('Orthogonal H->V', [1.0, 0.5, 0.8, 1])
        
        # Outer horizontal ScrollView - explicit size
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),  # Fixed viewport size
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.6, 0.8],
            smooth_scroll_end=10
        )
        
        outer_content = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_x=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_width=outer_content.setter('width'))
        
        # Add 5 inner vertical ScrollViews (more than fits)
        for i in range(5):
            inner_sv = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint_x=None,
                width=dp(120),
                bar_width=dp(6),
                bar_color=[1.0, 0.3, 0.5, 0.8]
            )
            
            inner_content = GridLayout(
                cols=1,
                spacing=dp(5),
                size_hint_y=None,
                padding=dp(5)
            )
            inner_content.bind(minimum_height=inner_content.setter('height'))
            
            for j in range(10):
                btn = Button(
                    text=f'C{i+1}\n{j+1}',
                    size_hint_y=None,
                    height=dp(45),
                    background_color=[0.8, 0.2 + i*0.12, 0.5, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_xy_nested(self):
        """XY Nested: XY->XY (both scroll in both directions)"""
        panel = self._create_panel_container('XY Nested\n(XY->XY)', [0.8, 0.3, 1.0, 1])
        
        # Outer XY ScrollView - explicit size
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),  # Fixed viewport size
            bar_width=dp(8),
            bar_color=[0.5, 0.3, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        outer_content = GridLayout(
            cols=3,  # 3x3 grid for more content
            spacing=dp(10),
            size_hint=(None, None),
            padding=dp(5)
        )
        outer_content.bind(minimum_width=outer_content.setter('width'))
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Add 9 inner XY ScrollViews (3x3 grid, definitely more than fits)
        for i in range(9):
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                size=(dp(200), dp(170)),  # Larger to force more outer scrolling
                bar_width=dp(6),
                bar_color=[1.0, 0.6, 0.3, 0.8]
            )
            
            inner_content = GridLayout(
                cols=5,  # 5 columns to force horizontal scrolling
                spacing=dp(5),
                size_hint=(None, None),
                padding=dp(5)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            inner_content.bind(minimum_height=inner_content.setter('height'))
            
            for j in range(30):  # 6 rows x 5 cols = 30 buttons
                btn = Button(
                    text=f'XY{i+1}\n{j+1}',
                    size_hint=(None, None),
                    size=(dp(60), dp(50)),  # Slightly larger buttons
                    background_color=[0.3 + (i%3)*0.2, 0.4, 0.8 - (i//3)*0.1, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_mixed_xy_h(self):
        """Mixed: XY->H (outer XY, inner horizontal)"""
        panel = self._create_panel_container('Mixed XY->H', [1.0, 1.0, 0.3, 1])
        
        # Outer XY ScrollView - explicit size
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),  # Fixed viewport size
            bar_width=dp(8),
            bar_color=[0.6, 0.8, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint=(None, None),
            padding=dp(5)
        )
        outer_content.bind(minimum_width=outer_content.setter('width'))
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Add 5 inner horizontal ScrollViews (wider than viewport for X scrolling)
        for i in range(5):
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                size=(dp(500), dp(100)),  # Wider than viewport (400) for outer X scrolling
                bar_width=dp(6),
                bar_color=[1.0, 0.7, 0.3, 0.8]
            )
            
            inner_content = BoxLayout(
                orientation='horizontal',
                spacing=dp(5),
                size_hint_x=None,
                padding=dp(5)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            
            for j in range(10):
                btn = Button(
                    text=f'XH{i+1}\n{j+1}',
                    size_hint_x=None,
                    width=dp(60),
                    background_color=[0.9, 0.5 - i*0.08, 0.3, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_mixed_xy_v(self):
        """Mixed: XY->XY->V (3-level: outer XY, middle XY, inner vertical)
        
        Full 3-level XY->XY->V configuration.
        GridLayout was the issue, not StencilView depth!
        """
        panel = self._create_panel_container('Mixed XY->V', [0.3, 1.0, 1.0, 1])
        
        # Outer XY ScrollView
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.6, 0.8, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        # Middle XY ScrollView content
        middle_content = GridLayout(
            cols=5,  # 5 columns for wider content
            spacing=dp(10),
            size_hint=(None, None),
            padding=dp(5)
        )
        middle_content.bind(minimum_width=middle_content.setter('width'))
        middle_content.bind(minimum_height=middle_content.setter('height'))
        
        # Add 15 inner vertical ScrollViews (3 rows x 5 cols for more width)
        for i in range(15):
            inner_sv = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                size=(dp(130), dp(200)),  # Increased height from 180 to 200
                bar_width=dp(6),
                bar_color=[0.3, 1.0, 0.7, 0.8]
            )
            
            inner_content = GridLayout(
                cols=1,
                spacing=dp(5),
                size_hint_y=None,
                padding=dp(5)
            )
            inner_content.bind(minimum_height=inner_content.setter('height'))
            
            for j in range(12):
                btn = Button(
                    text=f'C{i+1}\n{j+1}',
                    size_hint_y=None,
                    height=dp(50),
                    background_color=[0.3, 0.9, 0.5 - (i%3)*0.1, 1],
                    on_press=lambda x, idx=i, jdx=j: print(f'XY->XY->V: Cell {idx+1}, Button {jdx+1}')
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            middle_content.add_widget(inner_sv)
        
        outer_sv.add_widget(middle_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_3level_vertical(self):
        """3-Level Parallel Vertical: V->V->V"""
        panel = self._create_panel_container('3-Level Vertical\n(V->V->V)', [1.0, 0.3, 0.3, 1])
        
        # Outer vertical ScrollView (Level 1) - explicit size
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),  # Fixed viewport size
            bar_width=dp(8),
            bar_color=[1.0, 0.3, 0.3, 0.8],
            smooth_scroll_end=10
        )
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Middle vertical ScrollView (Level 2)
        middle_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint_y=None,
            height=dp(200),
            bar_width=dp(7),
            bar_color=[1.0, 0.5, 0.5, 0.8]
        )
        
        middle_content = GridLayout(
            cols=1,
            spacing=dp(6),
            size_hint_y=None,
            padding=dp(5)
        )
        middle_content.bind(minimum_height=middle_content.setter('height'))
        
        # Inner vertical ScrollView (Level 3)
        inner_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint_y=None,
            height=dp(120),
            bar_width=dp(6),
            bar_color=[1.0, 0.7, 0.7, 0.8]
        )
        
        inner_content = GridLayout(
            cols=1,
            spacing=dp(4),
            size_hint_y=None,
            padding=dp(5)
        )
        inner_content.bind(minimum_height=inner_content.setter('height'))
        
        # Innermost buttons
        for i in range(8):
            btn = Button(
                text=f'L3-{i+1}',
                size_hint_y=None,
                height=dp(35),
                background_color=[0.8, 0.2, 0.2, 1]
            )
            inner_content.add_widget(btn)
        
        inner_sv.add_widget(inner_content)
        middle_content.add_widget(inner_sv)
        
        # Add buttons to middle level
        for i in range(10):
            btn = Button(
                text=f'L2-{i+1}',
                size_hint_y=None,
                height=dp(35),
                background_color=[0.6, 0.2, 0.2, 1]
            )
            middle_content.add_widget(btn)
        
        middle_sv.add_widget(middle_content)
        outer_content.add_widget(middle_sv)
        
        # Add more buttons to outer level to ensure scrolling
        for i in range(8):  # More buttons to exceed viewport height
            btn = Button(
                text=f'L1-{i+1}',
                size_hint_y=None,
                height=dp(45),
                background_color=[0.4, 0.2, 0.2, 1]
            )
            outer_content.add_widget(btn)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_3level_orthogonal(self):
        """3-Level Orthogonal: V->H->V"""
        panel = self._create_panel_container('3-Level Orthog\n(V->H->V)', [0.3, 1.0, 0.3, 1])
        
        # Outer vertical ScrollView (Level 1) - explicit size
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),  # Fixed viewport size
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.3, 0.8],
            smooth_scroll_end=10
        )
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Middle horizontal ScrollView (Level 2)
        middle_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            size_hint_y=None,
            height=dp(200),
            bar_width=dp(7),
            bar_color=[0.5, 1.0, 0.5, 0.8]
        )
        
        middle_content = BoxLayout(
            orientation='horizontal',
            spacing=dp(6),
            size_hint_x=None,
            padding=dp(5)
        )
        middle_content.bind(minimum_width=middle_content.setter('width'))
        
        # Inner vertical ScrollView (Level 3)
        inner_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint_x=None,
            width=dp(120),
            bar_width=dp(6),
            bar_color=[0.7, 1.0, 0.7, 0.8]
        )
        
        inner_content = GridLayout(
            cols=1,
            spacing=dp(4),
            size_hint_y=None,
            padding=dp(5)
        )
        inner_content.bind(minimum_height=inner_content.setter('height'))
        
        # Innermost buttons
        for i in range(8):
            btn = Button(
                text=f'L3\n{i+1}',
                size_hint_y=None,
                height=dp(45),
                background_color=[0.2, 0.6, 0.2, 1]
            )
            inner_content.add_widget(btn)
        
        inner_sv.add_widget(inner_content)
        middle_content.add_widget(inner_sv)
        
        # Add some buttons to middle level
        for i in range(8):
            btn = Button(
                text=f'L2-{i+1}',
                size_hint_x=None,
                width=dp(80),
                background_color=[0.2, 0.5, 0.2, 1]
            )
            middle_content.add_widget(btn)
        
        middle_sv.add_widget(middle_content)
        outer_content.add_widget(middle_sv)
        
        # Add more buttons to outer level to ensure scrolling
        for i in range(8):  # More buttons to exceed viewport height
            btn = Button(
                text=f'Outer-{i+1}',
                size_hint_y=None,
                height=dp(45),
                background_color=[0.2, 0.3, 0.2, 1]
            )
            outer_content.add_widget(btn)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel


if __name__ == '__main__':
    MonsterNestingDemo().run()

