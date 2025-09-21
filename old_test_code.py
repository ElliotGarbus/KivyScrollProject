import kivy
kivy.require('1.8.1')

from kivy.app import App
from kivy.lang import Builder

import sys

if 'horizontal' in sys.argv:
    sys.argv.remove('horizontal')
    fmt = {
        'horizontal': 'vertical',
        'x': 'y',
        'y': 'x',
        'width': 'height',
        'height': 'width',
        'col': 'row',
        'row': 'col',
    }
else:
    fmt = {
        'horizontal': 'horizontal',
        'x': 'x',
        'y': 'y',
        'width': 'width',
        'height': 'height',
        'col': 'col',
        'row': 'row',
    }

root = Builder.load_string('''
BoxLayout:
    orientation: '{horizontal}'
    BoxLayout:
        orientation: '{horizontal}'
        size_hint_{x}: None
        {width}: 0

        Widget:
            id: quarter
        Widget
        Widget
        BoxLayout:
            orientation: '{horizontal}'
            Widget:
                id: eighth
            Widget
    ScrollView:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 0.3
            Rectangle:
                pos: self.pos
                size: self.size

        GridLayout:
            {col}s: 1
            size_hint_{y}: None
            {height}: self.minimum_{height}
            {row}_default_{height}: quarter.{height}
            {row}_force_default: True

            Widget

            BoxLayout:
                orientation: '{horizontal}'
                canvas.before:
                    Color:
                        rgba: 1, 0, 0, 0.5
                    Rectangle:
                        pos: self.pos
                        size: self.size

                Widget

                ScrollView:
                    GridLayout:
                        {col}s: 1
                        size_hint_{y}: None
                        size_hint_{x}: 2.0
                        {height}: self.minimum_{height}
                        {row}_default_{height}: eighth.{height}
                        {row}_force_default: True

                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size

                        Widget

                        Label:
                            text: 'Hi!'

                            canvas.before:
                                Color:
                                    rgba: 0, 0, 1, 0.5
                                Rectangle:
                                    pos: self.pos
                                    size: self.size

                        Widget

                Widget

            Widget
'''.format(**fmt))

class TestApp(App):
    def build(self):
        return root

if __name__ == '__main__':
    TestApp().run()