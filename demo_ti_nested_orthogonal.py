"""
Demo: Nested Orthogonal ScrollViews with TextInputs
Testing focus handling in nested ScrollViews where outer is horizontal and inner is vertical.
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

from updated_sv_no_manager import ScrollView


class InnerTextInputScrollView(ScrollView):
    """Inner ScrollView with vertical scrolling and TextInputs"""
    def __init__(self, panel_index, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True  # Inner ScrollView scrolls vertically
        self.bar_width = dp(6)
        self.scroll_type = ['bars', 'content']
        self.size_hint_y = None
        self.height = dp(300)  # Fixed height for inner scroll
        self.size_hint_x = None
        self.width = dp(350)  # Make panels wider
        
        # Create content layout
        content = GridLayout(
            cols=1, 
            size_hint_y=None, 
            size_hint_x=None,
            padding=dp(12), 
            spacing=dp(8)
        )
        content.bind(minimum_height=content.setter('height'))
        content.bind(minimum_width=content.setter('width'))
        
        # Add panel title
        title = Label(
            text=f"Panel {panel_index + 1} - TextInputs",
            size_hint=(None, None),
            width=dp(150),
            height=dp(30),
            color=(0.2, 0.6, 1, 1),
            font_size=dp(16),
            bold=True
        )
        content.add_widget(title)
        
        # Add TextInputs for this panel
        for j in range(1, 12):  # 11 TextInputs per panel
            # Create container for TextInput with label
            input_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                size_hint_x=None,
                height=dp(45),
                spacing=dp(2)
            )
            
            # Label for the TextInput
            label = Label(
                text=f"Input {j:2d}:",
                size_hint_y=None,
                height=dp(18),
                color=(0.4, 0.4, 0.4, 1),
                font_size=dp(12),
                halign='left'
            )
            input_container.add_widget(label)
            
            # The TextInput itself
            text_input = TextInput(
                text=f"Panel{panel_index + 1}_Input{j}",
                size_hint_y=None,
                height=dp(25),
                multiline=False,
                font_size=dp(12),
                hint_text=f"Enter text for panel {panel_index + 1}, input {j}...",
                background_color=(0.98, 0.98, 0.98, 1),
                foreground_color=(0.2, 0.2, 0.2, 1),
                write_tab=False
            )
            
            # Add focus event handlers
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
        
        # Bind scrollview width to content width
        content.bind(width=self.setter('width'))
    
    def on_textinput_focus(self, instance, focused):
        """Handle TextInput focus events for debugging"""
        if focused:
            print(f"Panel TextInput '{instance.text[:20]}' gained focus")
            # Ensure the focused TextInput is visible in the inner scroll
            self.scroll_to(instance.parent, animate=True)
        else:
            print(f"Panel TextInput '{instance.text[:20]}' lost focus")
    
    def on_textinput_text(self, instance, text):
        """Handle TextInput text changes"""
        print(f"Panel TextInput text changed: '{text[:15]}{'...' if len(text) > 15 else ''}'")


class OuterTextInputScrollView(ScrollView):
    """Outer ScrollView with horizontal scrolling containing multiple panels"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = True   # Outer ScrollView scrolls horizontally
        self.do_scroll_y = False  # No vertical scrolling for outer
        self.bar_width = dp(8)
        self.scroll_type = ['bars', 'content']
        
        # Create horizontal content layout
        content = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(16),
            padding=dp(16)
        )
        content.bind(minimum_width=content.setter('width'))
        
        # Add title panel
        title_panel = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(200),
            spacing=dp(8)
        )
        
        title = Label(
            text="Nested Orthogonal\nScrollViews\nwith TextInputs",
            size_hint_y=None,
            height=dp(100),
            color=(0.2, 0.2, 0.8, 1),
            font_size=dp(16),
            bold=True,
            halign='center',
            valign='middle'
        )
        title.bind(texture_size=title.setter('size'))
        title_panel.add_widget(title)
        
        instructions = Label(
            text="Test focus handling:\n"
                 "• Horizontal scroll between 10 panels\n"
                 "• Vertical scroll within panels\n"
                 "• Click TextInputs to focus\n"
                 "• Use Tab to navigate\n"
                 "• Check console for focus events\n"
                 "• Wider panels for better testing",
            size_hint_y=1,
            color=(0.4, 0.4, 0.4, 1),
            font_size=dp(12),
            halign='left',
            valign='top'
        )
        title_panel.add_widget(instructions)
        
        content.add_widget(title_panel)
        
        # Add multiple panels with TextInputs
        for i in range(10):  # 10 panels
            panel = InnerTextInputScrollView(panel_index=i)
            content.add_widget(panel)
        
        self.add_widget(content)


class NestedTextInputApp(App):
    def build(self):
        return OuterTextInputScrollView()


if __name__ == '__main__':
    NestedTextInputApp().run()

