"""
Demo showing XY outer with single-axis inner ScrollViews
Left side: XY outer with Horizontal inner
Right side: XY outer with Vertical inner
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from updated_sv_no_manager import ScrollView


class NestedXYMixedDemo(App):
    def build(self):
        main_layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        
        # Left side: XY outer with Horizontal inner
        left_panel = self._create_xy_horizontal_panel()
        main_layout.add_widget(left_panel)
        
        # Right side: XY outer with Vertical inner
        right_panel = self._create_xy_vertical_panel()
        main_layout.add_widget(right_panel)
        
        return main_layout
    
    def _create_xy_horizontal_panel(self):
        """Create XY outer with Horizontal inner scrollviews"""
        # Outer ScrollView: XY (both axes)
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        # Container for the outer scrollview content
        outer_container = GridLayout(
            cols=1,
            spacing=dp(20),
            size_hint=(None, None),
            padding=dp(10)
        )
        outer_container.bind(minimum_width=outer_container.setter('width'))
        outer_container.bind(minimum_height=outer_container.setter('height'))
        
        # Add title
        title = Label(
            text='XY Outer - Horizontal Inner\n(Outer scrolls both axes, Inner scrolls X only)',
            size_hint=(None, None),
            width=dp(400),
            height=dp(60),
            color=[1, 1, 0, 1],
            bold=True,
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        outer_container.add_widget(title)
        
        # Add multiple rows with horizontal scrollviews
        for i in range(8):
            # Inner ScrollView: Horizontal only
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                width=dp(350),
                height=dp(120),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8],
                smooth_scroll_end=10
            )
            
            inner_content = BoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_x=None
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            
            # Add label
            label = Label(
                text=f'Row {i+1}',
                size_hint_x=None,
                width=dp(80),
                color=[1, 1, 1, 1],
                bold=True
            )
            inner_content.add_widget(label)
            
            # Add buttons
            for j in range(15):
                btn = Button(
                    text=f'Btn {j+1}',
                    size_hint_x=None,
                    width=dp(100),
                    height=dp(80),
                    background_color=[0.2 + (i * 0.1) % 0.8, 0.3, 0.7, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_container.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_container)
        
        return outer_sv
    
    def _create_xy_vertical_panel(self):
        """Create XY outer with Vertical inner scrollviews"""
        # Outer ScrollView: XY (both axes)
        outer_sv = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.6, 0.8],
            smooth_scroll_end=10
        )
        
        # Main container with vertical layout for title and content
        main_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            spacing=dp(10),
            padding=dp(10)
        )
        main_container.bind(minimum_width=main_container.setter('width'))
        main_container.bind(minimum_height=main_container.setter('height'))
        
        # Add title
        title = Label(
            text='XY Outer - Vertical Inner\n(Outer scrolls both axes, Inner scrolls Y only)',
            size_hint=(None, None),
            width=dp(900),
            height=dp(50),
            color=[1, 1, 0, 1],
            bold=True,
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        main_container.add_widget(title)
        
        # Container for the columns
        columns_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint=(None, None)
        )
        columns_container.bind(minimum_width=columns_container.setter('width'))
        columns_container.bind(minimum_height=columns_container.setter('height'))
        
        # Add multiple columns with vertical scrollviews
        for i in range(6):
            # Inner ScrollView: Vertical only
            inner_sv = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint=(None, None),
                width=dp(150),
                height=dp(400),
                bar_width=dp(6),
                bar_color=[1.0, 0.3, 0.5, 0.8],
                smooth_scroll_end=10
            )
            
            inner_content = GridLayout(
                cols=1,
                spacing=dp(10),
                size_hint_y=None
            )
            inner_content.bind(minimum_height=inner_content.setter('height'))
            
            # Add label
            label = Label(
                text=f'Col {i+1}',
                size_hint_y=None,
                height=dp(40),
                color=[1, 1, 1, 1],
                bold=True
            )
            inner_content.add_widget(label)
            
            # Add buttons
            for j in range(20):
                btn = Button(
                    text=f'Item {j+1}',
                    size_hint_y=None,
                    height=dp(60),
                    background_color=[0.7, 0.3, 0.2 + (i * 0.1) % 0.8, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            columns_container.add_widget(inner_sv)
        
        # Add the columns container to the main container
        main_container.add_widget(columns_container)
        
        outer_sv.add_widget(main_container)
        
        return outer_sv


if __name__ == '__main__':
    NestedXYMixedDemo().run()

