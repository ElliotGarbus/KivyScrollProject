"""
test_scroll_events.py

A diagnostic tool to test on_scroll events in nested orthogonal ScrollViews.
Uses color-coded console output to track events from both ScrollViews.

Color scheme:
- Horizontal ScrollView (outer): Cyan
- Vertical ScrollView (inner): Magenta
- on_scroll_start: Green text
- on_scroll_stop: Red text
- on_scroll_move: Default color
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from updated_sv import ScrollView
from nested_scrollview_manager import NestedScrollViewManager

# ANSI color codes for terminal output
class Colors:
    CYAN = '\033[96m'       # Horizontal ScrollView
    MAGENTA = '\033[95m'    # Vertical ScrollView
    GREEN = '\033[92m'      # on_scroll_start
    RED = '\033[91m'        # on_scroll_stop
    RESET = '\033[0m'       # Reset to default
    BOLD = '\033[1m'


class ScrollEventTestApp(App):
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Info panel
        info_panel = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=5)
        title = Label(
            text='[b]Nested Orthogonal ScrollView Event Test[/b]\n'
                 'Vertical (outer) + Horizontal (inner)',
            markup=True,
            size_hint_y=0.4
        )
        subtitle = Label(
            text='Watch console for color-coded event output:\n'
                 '[color=00ffff]Cyan=Horizontal[/color] | '
                 '[color=ff00ff]Magenta=Vertical[/color] | '
                 '[color=00ff00]Green=Start[/color] | '
                 '[color=ff0000]Red=Stop[/color]',
            markup=True,
            size_hint_y=0.6
        )
        info_panel.add_widget(title)
        info_panel.add_widget(subtitle)
        
        # Create nested ScrollView setup using NestedScrollViewManager
        # Pattern: Vertical outer + Horizontal inner (like left side of demo_nested_orthogonal)
        manager = NestedScrollViewManager(size_hint=(1, 1))
        
        # Outer ScrollView (Vertical)
        self.outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=8,
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
        
        # Create multiple horizontal ScrollViews (inner) within the vertical outer
        for i in range(8):
            inner_sv = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint_y=None,
                height=120,
                bar_width=6,
                bar_color=[1.0, 0.5, 0.3, 0.8],
                smooth_scroll_end=10
            )
            # Store row number as a custom attribute for identification
            inner_sv.row_number = i + 1
            
            # Horizontal content for inner ScrollView
            inner_content = BoxLayout(
                orientation='horizontal',
                spacing=10,
                size_hint_x=None
            )
            inner_content.bind(minimum_width=inner_content.setter('width'))
            
            # Add label
            label = Label(
                text=f'Row {i+1} - Horizontal Scroll',
                size_hint_x=None,
                width=200,
                height=30,
                color=[1, 1, 1, 1],
                bold=True
            )
            inner_content.add_widget(label)
            
            # Add buttons to horizontal ScrollView
            for j in range(15):
                btn = Button(
                    text=f'Btn {j+1}',
                    size_hint_x=None,
                    width=100,
                    height=80,
                    background_color=[0.2 + (i * 0.1) % 0.8, 0.3, 0.7, 1]
                )
                inner_content.add_widget(btn)
            
            inner_sv.add_widget(inner_content)
            outer_content.add_widget(inner_sv)
            
            # Bind events for this inner ScrollView
            inner_sv.bind(on_scroll_start=self.on_horizontal_scroll_start)
            inner_sv.bind(on_scroll_move=self.on_horizontal_scroll_move)
            inner_sv.bind(on_scroll_stop=self.on_horizontal_scroll_stop)
        
        self.outer_sv.add_widget(outer_content)
        manager.add_widget(self.outer_sv)
        
        # Bind scroll events for outer (vertical) ScrollView
        self.outer_sv.bind(on_scroll_start=self.on_vertical_scroll_start)
        self.outer_sv.bind(on_scroll_move=self.on_vertical_scroll_move)
        self.outer_sv.bind(on_scroll_stop=self.on_vertical_scroll_stop)
        
        # Assemble the UI
        main_layout.add_widget(info_panel)
        main_layout.add_widget(manager)
        
        print(f"\n{Colors.BOLD}=== Scroll Event Test Started ==={Colors.RESET}\n")
        
        return main_layout
    
    # Horizontal ScrollView (Inner) event handlers
    def on_horizontal_scroll_start(self, instance):
        row_num = getattr(instance, 'row_number', '?')
        print(f"{Colors.CYAN}{Colors.GREEN}[Row {row_num}] on_scroll_start{Colors.RESET}")
        print(f"{Colors.CYAN}  scroll_x: {instance.scroll_x:.4f}, scroll_y: {instance.scroll_y:.4f}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}\n")
    
    def on_horizontal_scroll_move(self, instance):
        row_num = getattr(instance, 'row_number', '?')
        print(f"{Colors.CYAN}[Row {row_num}] on_scroll_move{Colors.RESET}")
        print(f"{Colors.CYAN}  scroll_x: {instance.scroll_x:.4f}, scroll_y: {instance.scroll_y:.4f}{Colors.RESET}")
    
    def on_horizontal_scroll_stop(self, instance):
        row_num = getattr(instance, 'row_number', '?')
        vel_x = instance.effect_x.velocity if instance.effect_x else 0
        vel_y = instance.effect_y.velocity if instance.effect_y else 0
        print(f"{Colors.CYAN}{Colors.RED}[Row {row_num}] on_scroll_stop{Colors.RESET}")
        print(f"{Colors.CYAN}  scroll_x: {instance.scroll_x:.4f}, scroll_y: {instance.scroll_y:.4f}{Colors.RESET}")
        print(f"{Colors.CYAN}  velocity_x: {vel_x:.6f}, velocity_y: {vel_y:.6f}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}\n")
    
    # Vertical ScrollView (Outer) event handlers
    def on_vertical_scroll_start(self, instance):
        print(f"{Colors.MAGENTA}{Colors.GREEN}[VERTICAL] on_scroll_start{Colors.RESET}")
        print(f"{Colors.MAGENTA}  scroll_x: {instance.scroll_x:.4f}, scroll_y: {instance.scroll_y:.4f}{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'─' * 50}{Colors.RESET}\n")
    
    def on_vertical_scroll_move(self, instance):
        print(f"{Colors.MAGENTA}[VERTICAL] on_scroll_move{Colors.RESET}")
        print(f"{Colors.MAGENTA}  scroll_x: {instance.scroll_x:.4f}, scroll_y: {instance.scroll_y:.4f}{Colors.RESET}")
    
    def on_vertical_scroll_stop(self, instance):
        vel_x = instance.effect_x.velocity if instance.effect_x else 0
        vel_y = instance.effect_y.velocity if instance.effect_y else 0
        print(f"{Colors.MAGENTA}{Colors.RED}[VERTICAL] on_scroll_stop{Colors.RESET}")
        print(f"{Colors.MAGENTA}  scroll_x: {instance.scroll_x:.4f}, scroll_y: {instance.scroll_y:.4f}{Colors.RESET}")
        print(f"{Colors.MAGENTA}  velocity_x: {vel_x:.6f}, velocity_y: {vel_y:.6f}{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'─' * 50}{Colors.RESET}\n")


if __name__ == '__main__':
    ScrollEventTestApp().run()

