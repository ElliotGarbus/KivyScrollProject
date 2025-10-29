"""
Simple RecycleView Demo, using new ScrollView
===================================================
Demonstrates a simple RecycleView using the new ScrollView
"""

# CRITICAL: Monkey patch ScrollView BEFORE RecycleView imports it
# RecycleView does "from kivy.uix.scrollview import ScrollView"
# So we need to replace ScrollView in that module before RecycleView loads

import kivy.uix.scrollview
import scrollview

# Replace ScrollView in the kivy.uix.scrollview module
kivy.uix.scrollview.ScrollView = scrollview.ScrollView

# Also register with Factory for kv language
from kivy.factory import Factory
Factory.unregister('ScrollView')
Factory.register('ScrollView', cls=scrollview.ScrollView)

# NOW we can import RecycleView - it will import our custom ScrollView
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty




kv = '''
<TwoButtons>:
# This class is used as the viewclass in the RecycleView
# The means this widget will be instanced to view one element of data from the data list.
# The RecycleView data list is a list of dictionaries.  The keys in the dictionary specify the 
# attributes of the widget.
    Button:
        text: root.left_text
        on_release: print(f'Button {self.text} pressed') 
    Button:
        text: root.right_text
        on_release: print(f'Button {self.text} pressed') 
        
BoxLayout:
    orientation: 'vertical'
    Button:
        size_hint_y: None
        height: 48
        text: 'Add widget to RV list'
        on_release: rv.add()
    
    RV:                          # A RecycleView
        id: rv
        viewclass: 'TwoButtons'  # The view class is TwoButtons, defined above.
        scroll_type: ['bars', 'content']
        bar_width: 10
        RecycleBoxLayout:        
            # This layout is used to hold the Recycle widgets
            default_size: None, dp(48)   # This sets the height of the BoxLayout that holds a TwoButtons instance.
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height   # To scroll you need to set the layout height.
            orientation: 'vertical'
'''


class TwoButtons(BoxLayout):  # The viewclass definition, and property definitions.
    left_text = StringProperty()
    right_text = StringProperty()


class RV(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('RV init')
        self.data = [{'left_text': f'Left {i}', 'right_text': f'Right {i}'} for i in range(2)]
        # This list comprehension is used to create the data list for this simple example.
        # The data created looks like:
        # [{'left_text': 'Left 0', 'right_text': 'Right 0'}, {'left_text': 'Left 1', 'right_text': 'Right 1'},
        # {'left_text': 'Left 2', 'right_text': 'Right 2'}, {'left_text': 'Left 3'},...
        # notice the keys in the dictionary correspond to the kivy properties in the TwoButtons class.
        # The data needs to be in this kind of list of dictionary formats.  The RecycleView instances the
        # widgets, and populates them with data from this list.

    def add(self):
        dl = len(self.data)
        self.data.extend([{'left_text': f'Added Left {i}',
                           'right_text': f'Added Right {i}'} for i in range(dl, dl + 1)])


class RVTwoApp(App):
    def build(self):
        return Builder.load_string(kv)


RVTwoApp().run()
