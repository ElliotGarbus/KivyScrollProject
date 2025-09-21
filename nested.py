from kivy.app import App
from my_scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp


"""
Test case for nested ScrollView
The outer_box is a BoxLayout in the outer scrollview
The inner_box is a BoxLaout  that contains a button and the inner ScrollView that contains a Label.
The vertical scroll will NOT work on top of the horizontal Scroll.  The Horizontal Scroll is eating the touch.
The vertical Scroll will work on the buttons, or in the vertical scroll text area.
"""

class NestedScrollApp(App):
    def build(self):
        # Outer vertical ScrollView
        root = ScrollView(
            do_scroll_x=False, 
            do_scroll_y=True
        )
        
        outer_box = BoxLayout(orientation='vertical', size_hint_y=None)
        root.add_widget(outer_box)
        outer_box.bind(minimum_height=outer_box.setter('height'))
        
        # Add some rows with horizontal ScrollViews
        for i in range(10):
            inner_box = BoxLayout(size_hint=(1, None), height=dp(30))
            button = Button(text='Vertical Scroll Here', size_hint_x=None, width=dp(200))
            inner_box.add_widget(button)
            
            # Inner horizontal ScrollView
            sv = ScrollView(
                do_scroll_x=True, 
                do_scroll_y=False
            )
            label = Label(text=f'Horizontal Scroll {i:2d} '*10, size_hint_x=None, padding=dp(5))
            label.texture_update()
            label.width = label.texture_size[0]
            sv.add_widget(label)
            inner_box.add_widget(sv)
            outer_box.add_widget(inner_box)
            
        # Add some additional vertical content
        for i in range(20):
            label = Label(size_hint_y=None, height=dp(30), text=f'Vertical Scroll {i:2d} ')
            outer_box.add_widget(label)
            
        return root
            

NestedScrollApp().run()
