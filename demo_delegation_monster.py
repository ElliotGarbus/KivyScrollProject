"""
Delegation Monster Demo - Testing delegate_to_outer Property
=============================================================
Based on Monster Nesting Demo, with a toggle button to control
the delegate_to_outer property of all outermost ScrollViews in each panel.

When delegate_to_outer is True (default):
- Orthogonal cross-axis gestures delegate to outer XY
- Parallel boundary scrolling delegates to outer XY

When delegate_to_outer is False:
- ScrollViews are isolated, no delegation to outer XY
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.metrics import dp
from scrollview import ScrollView


class DelegationMonsterDemo(App):
    """Main app with XY outer ScrollView and toggle to control delegate_to_outer."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Store references to all outermost ScrollViews in panels
        self.panel_scrollviews = []
    
    def build(self):
        # Root container
        root = BoxLayout(orientation='vertical')
        
        # Toggle button at the top
        toggle_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            padding=dp(10),
            spacing=dp(10)
        )
        
        toggle_label = Label(
            text='delegate_to_outer:',
            size_hint_x=None,
            width=dp(150),
            color=[1, 1, 1, 1],
            bold=True,
            font_size='16sp'
        )
        
        toggle_button = ToggleButton(
            text='TRUE (Delegation Enabled)',
            state='down',  # Start in the 'down' state (True)
            size_hint_x=None,
            width=dp(250),
            background_color=[0.2, 0.8, 0.2, 1]
        )
        toggle_button.bind(on_press=self.on_toggle_delegation)
        
        info_label = Label(
            text='Toggle to enable/disable delegation to outer XY ScrollView',
            color=[0.7, 0.7, 0.7, 1],
            font_size='12sp',
            halign='left'
        )
        info_label.bind(size=info_label.setter('text_size'))
        
        toggle_container.add_widget(toggle_label)
        toggle_container.add_widget(toggle_button)
        toggle_container.add_widget(info_label)
        
        root.add_widget(toggle_container)
        
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
            text='Delegation Monster Demo - 12 Configurations',
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
        
        # Row 0 - Basic single ScrollViews
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
        root.add_widget(outer_sv)
        
        # Store the toggle button reference for updates
        self.toggle_button = toggle_button
        
        return root
    
    def on_toggle_delegation(self, instance):
        """Called when toggle button is pressed."""
        new_state = instance.state == 'down'
        
        # Update button appearance
        if new_state:
            instance.text = 'TRUE (Delegation Enabled)'
            instance.background_color = [0.2, 0.8, 0.2, 1]
        else:
            instance.text = 'FALSE (Delegation Disabled)'
            instance.background_color = [0.8, 0.2, 0.2, 1]
        
        # Update all panel scrollviews
        for sv in self.panel_scrollviews:
            sv.delegate_to_outer = new_state
        
        print(f"\n[DELEGATION] delegate_to_outer set to {new_state} for {len(self.panel_scrollviews)} ScrollViews\n")
    
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
        self.panel_scrollviews.append(sv)
        
        content = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        content.bind(minimum_height=content.setter('height'))
        
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
        self.panel_scrollviews.append(sv)
        
        content = BoxLayout(
            orientation='horizontal',
            spacing=dp(5),
            size_hint_x=None,
            padding=dp(5)
        )
        content.bind(minimum_width=content.setter('width'))
        
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
        self.panel_scrollviews.append(sv)
        
        content = GridLayout(
            cols=9,
            spacing=dp(5),
            size_hint=(None, None),
            padding=dp(5)
        )
        content.bind(minimum_width=content.setter('width'))
        content.bind(minimum_height=content.setter('height'))
        
        for i in range(99):
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
        """Parallel Vertical: V->V"""
        panel = self._create_panel_container('Parallel Vertical\n(V->V)', [0.3, 0.8, 1.0, 1])
        
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        self.panel_scrollviews.append(outer_sv)
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
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
        """Parallel Horizontal: H->H"""
        panel = self._create_panel_container('Parallel Horizontal\n(H->H)', [0.3, 1.0, 0.8, 1])
        
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.6, 0.8],
            smooth_scroll_end=10
        )
        self.panel_scrollviews.append(outer_sv)
        
        outer_content = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_x=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_width=outer_content.setter('width'))
        
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
        """Orthogonal: V->H"""
        panel = self._create_panel_container('Orthogonal V->H', [1.0, 0.8, 0.3, 1])
        
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        self.panel_scrollviews.append(outer_sv)
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
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
        """Orthogonal: H->V"""
        panel = self._create_panel_container('Orthogonal H->V', [1.0, 0.5, 0.8, 1])
        
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.6, 0.8],
            smooth_scroll_end=10
        )
        self.panel_scrollviews.append(outer_sv)
        
        outer_content = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_x=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_width=outer_content.setter('width'))
        
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
        """XY Nested: XY->XY"""
        panel = self._create_panel_container('XY Nested\n(XY->XY)', [0.8, 0.3, 1.0, 1])
        
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.5, 0.3, 1.0, 0.8],
            smooth_scroll_end=10
        )
        self.panel_scrollviews.append(outer_sv)
        
        outer_content = GridLayout(
            cols=3,
            spacing=dp(10),
            size_hint=(None, None),
            padding=dp(5)
        )
        outer_content.bind(minimum_width=outer_content.setter('width'))
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        for i in range(9):
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                size=(dp(200), dp(170)),
                bar_width=dp(6),
                bar_color=[1.0, 0.6, 0.3, 0.8]
            )
            
            inner_content = GridLayout(
                cols=5,
                spacing=dp(5),
                size_hint=(None, None),
                padding=dp(5)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            inner_content.bind(minimum_height=inner_content.setter('height'))
            
            for j in range(30):
                btn = Button(
                    text=f'XY{i+1}\n{j+1}',
                    size_hint=(None, None),
                    size=(dp(60), dp(50)),
                    background_color=[0.3 + (i%3)*0.2, 0.4, 0.8 - (i//3)*0.1, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_content)
        panel.add_widget(outer_sv)
        return panel
    
    def _create_mixed_xy_h(self):
        """Mixed: XY->H"""
        panel = self._create_panel_container('Mixed XY->H', [1.0, 1.0, 0.3, 1])
        
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
        self.panel_scrollviews.append(outer_sv)
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint=(None, None),
            padding=dp(5)
        )
        outer_content.bind(minimum_width=outer_content.setter('width'))
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        for i in range(5):
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                size=(dp(500), dp(100)),
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
        """Mixed: XY->V"""
        panel = self._create_panel_container('Mixed XY->V', [0.3, 1.0, 1.0, 1])
        
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
        self.panel_scrollviews.append(outer_sv)
        
        middle_content = GridLayout(
            cols=5,
            spacing=dp(10),
            size_hint=(None, None),
            padding=dp(5)
        )
        middle_content.bind(minimum_width=middle_content.setter('width'))
        middle_content.bind(minimum_height=middle_content.setter('height'))
        
        for i in range(15):
            inner_sv = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                size=(dp(130), dp(200)),
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
                    background_color=[0.3, 0.9, 0.5 - (i%3)*0.1, 1]
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
        
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[1.0, 0.3, 0.3, 0.8],
            smooth_scroll_end=10
        )
        self.panel_scrollviews.append(outer_sv)
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
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
        
        for i in range(8):
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
        
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            size_hint=(None, None),
            size=(dp(400), dp(390)),
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.3, 0.8],
            smooth_scroll_end=10
        )
        self.panel_scrollviews.append(outer_sv)
        
        outer_content = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(5)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
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
        
        for i in range(8):
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
    DelegationMonsterDemo().run()

