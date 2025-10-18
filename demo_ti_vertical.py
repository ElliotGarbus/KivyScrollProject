"""
Demo: Vertical ScrollView with TextInputs
Testing focus handling in a single vertical ScrollView with multiple TextInputs.
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

from updated_sv_no_manager import ScrollView


class TextInputScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True  # Vertical scrolling only
        self.bar_width = dp(8)
        self.scroll_type = ['bars', 'content']
        
        # Create content layout
        content = GridLayout(
            cols=1, 
            size_hint_y=None, 
            padding=dp(16), 
            spacing=dp(12)
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Add title
        title = Label(
            text="TextInput Focus Test - Vertical ScrollView",
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.2, 0.8, 1),
            font_size=dp(18),
            bold=True
        )
        content.add_widget(title)
        
        # Add instructions
        instructions = Label(
            text="Test focus handling by:\n"
                 "1. Scrolling to different TextInputs\n"
                 "2. Clicking to focus TextInputs\n"
                 "3. Using Tab to navigate between fields\n"
                 "4. Typing in focused TextInputs",
            size_hint_y=None,
            height=dp(80),
            color=(0.4, 0.4, 0.4, 1),
            font_size=dp(14),
            halign='left',
            valign='top'
        )
        instructions.bind(texture_size=instructions.setter('size'))
        content.add_widget(instructions)
        
        # Add multiple TextInputs with different configurations
        for i in range(1, 16):  # 15 TextInputs to ensure scrolling
            # Create a container for each TextInput with label
            input_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10)
            )
            
            # Label for the TextInput
            label = Label(
                text=f"Input {i:2d}:",
                size_hint_x=None,
                width=dp(80),
                color=(0.3, 0.3, 0.3, 1),
                font_size=dp(14)
            )
            input_container.add_widget(label)
            
            # The TextInput itself
            text_input = TextInput(
                text=f"Default text for input {i}",
                size_hint_x=1,
                multiline=False,
                font_size=dp(14),
                hint_text=f"Enter text for input {i}...",
                background_color=(0.95, 0.95, 0.95, 1),
                foreground_color=(0.2, 0.2, 0.2, 1),
                write_tab=False
            )
            
            # Add focus event handlers for testing
            text_input.bind(
                on_focus=self.on_textinput_focus,
                on_text=self.on_textinput_text
            )
            input_container.add_widget(text_input)
            
            content.add_widget(input_container)
        
        # Add some spacing at the end
        spacer = Label(text="", size_hint_y=None, height=dp(20))
        content.add_widget(spacer)
        
        self.add_widget(content)
    
    def on_textinput_focus(self, instance, focused):
        """Handle TextInput focus events for debugging"""
        if focused:
            print(f"TextInput '{instance.hint_text}' gained focus")
            # Ensure the focused TextInput is visible
            self.scroll_to(instance, animate=True)
        else:
            print(f"TextInput '{instance.hint_text}' lost focus")
    
    def on_textinput_text(self, instance, text):
        """Handle TextInput text changes"""
        print(f"TextInput text changed: '{text[:20]}{'...' if len(text) > 20 else ''}'")


class TextInputVerticalApp(App):
    def build(self):
        return TextInputScrollView()


if __name__ == '__main__':
    TextInputVerticalApp().run()

