"""
demo_single_slider.py

Demo showing a single vertical ScrollView with buttons, labels, and sliders.
Tests interaction between scrolling and slider widgets.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.metrics import dp
from scrollview import ScrollView


class SingleSliderDemo(App):
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='[b]Single ScrollView with Sliders Demo[/b]\n'
                 'Test scrolling interaction with slider widgets',
            markup=True,
            size_hint_y=None,
            height=60
        )
        main_layout.add_widget(title)
        
        # ScrollView
        scrollview = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(10),
            bar_color=[0.3, 0.6, 1.0, 0.8],
            smooth_scroll_end=10
        )
        
        # Content container
        content = GridLayout(
            cols=1,
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Create 20 rows, each with button, label, and slider
        for i in range(20):
            # Row container
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(80),
                spacing=dp(10)
            )
            
            # Button
            btn = Button(
                text=f'Row {i+1}',
                size_hint_x=0.2,
                background_color=[0.2 + (i * 0.04) % 0.8, 0.3, 0.7, 1]
            )
            row.add_widget(btn)
            
            # Label to show slider value
            value_label = Label(
                text='50',
                size_hint_x=0.15,
                color=[1, 1, 1, 1],
                bold=True
            )
            row.add_widget(value_label)
            
            # Slider
            slider = Slider(
                min=0,
                max=100,
                value=50,
                size_hint_x=0.65
            )
            
            # Bind slider to update label
            # Using a lambda with default argument to capture current label reference
            slider.bind(value=lambda instance, value, lbl=value_label: lbl.__setattr__('text', f'{int(value)}'))
            
            row.add_widget(slider)
            
            # Add row to content
            content.add_widget(row)
        
        scrollview.add_widget(content)
        main_layout.add_widget(scrollview)
        
        return main_layout


if __name__ == '__main__':
    SingleSliderDemo().run()

