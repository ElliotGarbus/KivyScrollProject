"""
Simple example of nested orthogonal ScrollViews for documentation.

This example demonstrates:
- Vertical outer ScrollView
- Horizontal inner ScrollViews
- Direct nesting of ScrollViews without manager
- Layout requirements for nested scrolling
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from scrollview import ScrollView


class NestedScrollApp(App):
    def build(self):
        # Create outer vertical ScrollView
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            smooth_scroll_end=10,
            bar_width='10dp',
            scroll_type=['bars', 'content']
        )
        
        # Outer content layout (MUST be a Layout widget)
        outer_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=20
        )
        outer_layout.bind(minimum_height=outer_layout.setter('height'))
        
        # Add several horizontal ScrollViews
        for i in range(5):
            # Create nested horizontal ScrollView
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                size_hint_y=None,
                height=120,
                smooth_scroll_end=10,
                bar_width='10dp',
                scroll_type=['bars', 'content']
            )
            
            # Inner content layout
            inner_layout = BoxLayout(
                orientation='horizontal',
                size_hint_x=None,
                spacing=10
            )
            inner_layout.bind(minimum_width=inner_layout.setter('width'))
            
            # Add horizontal scrolling buttons
            for j in range(10):
                btn = Button(
                    text=f'Button {i}-{j}',
                    size_hint_x=None,
                    width=100,
                    height=80
                )
                inner_layout.add_widget(btn)
            
            # Assemble inner ScrollView
            inner_sv.add_widget(inner_layout)
            outer_layout.add_widget(inner_sv)
        
        # Assemble the nested structure
        outer_sv.add_widget(outer_layout)
        
        return outer_sv


if __name__ == '__main__':
    NestedScrollApp().run()
