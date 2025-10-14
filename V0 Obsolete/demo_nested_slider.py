"""
demo_nested_slider.py

Demo showing nested orthogonal ScrollViews with buttons, labels, and sliders.
Tests interaction between nested scrolling and slider widgets.
Pattern: Vertical outer + Horizontal inner (like demo_nested_orthogonal.py)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.metrics import dp
from updated_sv import ScrollView
from nested_scrollview_manager import NestedScrollViewManager


class NestedSliderDemo(App):
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='[b]Nested Orthogonal ScrollView with Sliders Demo[/b]\n'
                 'Vertical (outer) + Horizontal (inner) - Test scrolling with sliders',
            markup=True,
            size_hint_y=None,
            height=60
        )
        main_layout.add_widget(title)
        
        # Create NestedScrollViewManager
        manager = NestedScrollViewManager(size_hint=(1, 1))
        
        # Outer ScrollView (Vertical)
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        # Outer content container (vertical layout with multiple horizontal ScrollViews)
        outer_content = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=None
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Create 8 horizontal ScrollViews (rows)
        for i in range(8):
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint_y=None,
                height=dp(140),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8],
                smooth_scroll_end=10
            )
            
            # Horizontal content for inner ScrollView
            inner_content = BoxLayout(
                orientation='horizontal',
                spacing=dp(15),
                size_hint_x=None,
                padding=dp(10)
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            
            # Add row label
            row_label = Label(
                text=f'Row {i+1}\nHorizontal Scroll ->',
                size_hint_x=None,
                width=dp(150),
                color=[1, 1, 1, 1],
                bold=True,
                halign='center'
            )
            inner_content.add_widget(row_label)
            
            # Create 10 items (each with button, label, slider) in horizontal row
            for j in range(10):
                # Item container (vertical layout)
                item = BoxLayout(
                    orientation='vertical',
                    size_hint_x=None,
                    width=dp(200),
                    spacing=dp(5)
                )
                
                # Button
                btn = Button(
                    text=f'Item {j+1}',
                    size_hint_y=None,
                    height=dp(40),
                    background_color=[0.2 + (i * 0.1) % 0.8, 0.3, 0.7, 1]
                )
                item.add_widget(btn)
                
                # Slider with label container
                slider_container = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(5)
                )
                
                # Value label
                value_label = Label(
                    text='50',
                    size_hint_x=None,
                    width=dp(40),
                    color=[1, 1, 1, 1],
                    bold=True
                )
                slider_container.add_widget(value_label)
                
                # Slider
                slider = Slider(
                    min=0,
                    max=100,
                    value=50,
                    size_hint_x=1
                )
                
                # Bind slider to update label
                slider.bind(value=lambda instance, value, lbl=value_label: lbl.__setattr__('text', f'{int(value)}'))
                
                slider_container.add_widget(slider)
                item.add_widget(slider_container)
                
                # Add item to horizontal content
                inner_content.add_widget(item)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
        
        outer_sv.add_widget(outer_content)
        manager.add_widget(outer_sv)
        main_layout.add_widget(manager)
        
        return main_layout


if __name__ == '__main__':
    NestedSliderDemo().run()

