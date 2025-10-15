"""
Demo showing single-axis outer with XY inner ScrollViews
Left side: Horizontal outer with XY inner
Right side: Vertical outer with XY inner
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from updated_sv_no_manager import ScrollView


class NestedSingleXYDemo(App):
    def build(self):
        main_layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        
        # Left side: Horizontal outer with XY inner
        left_panel = self._create_horizontal_xy_panel()
        main_layout.add_widget(left_panel)
        
        # Right side: Vertical outer with XY inner
        right_panel = self._create_vertical_xy_panel()
        main_layout.add_widget(right_panel)
        
        return main_layout
    
    def _create_horizontal_xy_panel(self):
        """Create Horizontal outer with XY inner scrollviews"""
        # Outer ScrollView: Horizontal only
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        # Container for the outer scrollview content
        outer_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_x=None,
            padding=dp(10)
        )
        outer_container.bind(minimum_width=outer_container.setter('width'))
        
        # Add title
        title = Label(
            text='Horizontal Outer - XY Inner\n(Outer scrolls X only, Inner scrolls both)',
            size_hint_x=None,
            width=dp(250),
            color=[1, 1, 0, 1],
            bold=True,
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        outer_container.add_widget(title)
        
        # Add multiple XY scrollviews horizontally
        for i in range(6):
            # Inner ScrollView: XY (both axes)
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                width=dp(300),
                height=dp(400),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8],
                smooth_scroll_end=10
            )
            
            # Create a container for header and grid
            panel_container = BoxLayout(
                orientation='vertical',
                spacing=dp(5),
                size_hint=(None, None),
                padding=dp(5)
            )
            panel_container.bind(minimum_width=panel_container.setter('width'))
            panel_container.bind(minimum_height=panel_container.setter('height'))
            
            # Add header
            header = Label(
                text=f'Panel {i+1} - XY Scroll',
                size_hint=(None, None),
                width=dp(340),
                height=dp(40),
                color=[1, 1, 1, 1],
                bold=True
            )
            panel_container.add_widget(header)
            
            # Grid for buttons
            inner_content = GridLayout(
                cols=4,
                spacing=dp(10),
                size_hint=(None, None),
                padding=dp(5)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            inner_content.bind(minimum_height=inner_content.setter('height'))
            
            # Add buttons in a grid
            for j in range(40):
                btn = Button(
                    text=f'{j+1}',
                    size_hint=(None, None),
                    width=dp(80),
                    height=dp(80),
                    background_color=[0.2 + (i * 0.1) % 0.8, 0.3, 0.7, 1]
                )
                inner_content.add_widget(btn)
            
            panel_container.add_widget(inner_content)
            inner_sv.add_widget(panel_container)
            outer_container.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_container)
        
        return outer_sv
    
    def _create_vertical_xy_panel(self):
        """Create Vertical outer with XY inner scrollviews"""
        # Outer ScrollView: Vertical only
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.6, 0.8],
            smooth_scroll_end=10
        )
        
        # Container for the outer scrollview content
        outer_container = GridLayout(
            cols=1,
            spacing=dp(20),
            size_hint_y=None,
            padding=dp(10)
        )
        outer_container.bind(minimum_height=outer_container.setter('height'))
        
        # Add title
        title = Label(
            text='Vertical Outer - XY Inner\n(Outer scrolls Y only, Inner scrolls both)',
            size_hint_y=None,
            height=dp(60),
            color=[1, 1, 0, 1],
            bold=True,
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        outer_container.add_widget(title)
        
        # Add multiple XY scrollviews vertically
        for i in range(6):
            # Inner ScrollView: XY (both axes)
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                width=dp(450),
                height=dp(250),
                bar_width=dp(6),
                bar_color=[1.0, 0.3, 0.5, 0.8],
                smooth_scroll_end=10
            )
            
            # Create a container for header and grid
            panel_container = BoxLayout(
                orientation='vertical',
                spacing=dp(5),
                size_hint=(None, None),
                padding=dp(5)
            )
            panel_container.bind(minimum_width=panel_container.setter('width'))
            panel_container.bind(minimum_height=panel_container.setter('height'))
            
            # Add header
            header = Label(
                text=f'Panel {i+1} - XY Scroll',
                size_hint=(None, None),
                width=dp(425),
                height=dp(40),
                color=[1, 1, 1, 1],
                bold=True
            )
            panel_container.add_widget(header)
            
            # Grid for buttons
            inner_content = GridLayout(
                cols=5,
                spacing=dp(10),
                size_hint=(None, None),
                padding=dp(5)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            inner_content.bind(minimum_height=inner_content.setter('height'))
            
            # Add buttons in a grid
            for j in range(50):
                btn = Button(
                    text=f'{j+1}',
                    size_hint=(None, None),
                    width=dp(80),
                    height=dp(80),
                    background_color=[0.7, 0.3, 0.2 + (i * 0.1) % 0.8, 1]
                )
                inner_content.add_widget(btn)
            
            panel_container.add_widget(inner_content)
            inner_sv.add_widget(panel_container)
            outer_container.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_container)
        
        return outer_sv


if __name__ == '__main__':
    NestedSingleXYDemo().run()

