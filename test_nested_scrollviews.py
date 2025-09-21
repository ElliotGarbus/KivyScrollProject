"""
Test file for demonstrating nested ScrollViews with orthogonal scrolling.
This test shows how the updated ScrollView implementation allows proper
nested scrolling when the scroll directions are perpendicular to each other.

Layout:
- Top level: Horizontal BoxLayout
- Left side: Vertical ScrollView containing multiple horizontal ScrollViews
- Right side: Horizontal ScrollView containing multiple vertical ScrollViews
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.metrics import dp
from updated_sv import ScrollView
from kivy.input.motionevent import MotionEvent
from functools import wraps
from kivy.core.window import Window
# --- Global grab/ungrab tracing ---
_orig_grab = MotionEvent.grab
_orig_ungrab = MotionEvent.ungrab


def _debug_grab(self, widget):
    try:
        before_list = getattr(self, "grab_list", []) or []
        before = len(before_list)
    except Exception:
        before = "?"
        before_list = []
    result = _orig_grab(self, widget)
    try:
        after_list = getattr(self, "grab_list", []) or []
        holders_after = [
            _name_of(w()) for w in after_list if callable(w) and w() is not None
        ]
        print(
            f"[GRAB CALL] touch={id(self)} widget={_name_of(widget)} holders_before={before} "
            f"holders_after={holders_after}"
        )
    except Exception:
        pass
    return result


def _debug_ungrab(self, widget):
    try:
        before_list = getattr(self, "grab_list", []) or []
        holders_before = [
            _name_of(w()) for w in before_list if callable(w) and w() is not None
        ]
    except Exception:
        holders_before = []
    result = _orig_ungrab(self, widget)
    try:
        after_list = getattr(self, "grab_list", []) or []
        holders_after = [
            _name_of(w()) for w in after_list if callable(w) and w() is not None
        ]
        print(
            f"[UNGRAB CALL] touch={id(self)} widget={_name_of(widget)} "
            f"holders_before={holders_before} holders_after={holders_after}"
        )
    except Exception:
        pass
    return result


MotionEvent.grab = _debug_grab
MotionEvent.ungrab = _debug_ungrab

# Track when grab_current is set/reset at the MotionEvent level
_orig_setattr = MotionEvent.__setattr__


def _debug_setattr(self, name, value):
    if name == "grab_current":
        try:
            who = _name_of(value) if value is not None else "None"
            print(f"[SET grab_current] touch={id(self)} -> {who}")
        except Exception:
            pass
    return _orig_setattr(self, name, value)


MotionEvent.__setattr__ = _debug_setattr



# --- External debug instrumentation (Idea 7): wrap on_touch_move ---

def _name_of(widget):
    try:
        return getattr(widget, "_debug_name", f"{widget.__class__.__name__}#{getattr(widget, 'uid', '?')}")
    except Exception:
        return str(widget)


_orig_move = ScrollView.on_touch_move
_orig_down = ScrollView.on_touch_down
_orig_change_mode = ScrollView._change_touch_mode
_orig_sim_down = ScrollView.simulate_touch_down
_orig_up = ScrollView.on_touch_up


@wraps(_orig_move)
def _debug_on_touch_move(self, touch):
    # If this ScrollView considers this touch as its active drag, it should
    # also be in the touch's grab_list. grab_current is only set during the
    # special grabbed-dispatch pass, so rely on grab_list membership here.
    try:
        if getattr(self, "_touch", None) is touch:
            gl = getattr(touch, "grab_list", []) or []
            is_grabbed = any(w() is self for w in gl)
            if len(gl) > 1:
                holders = [
                    _name_of(w()) for w in gl if callable(w) and w() is not None
                ]
                print(
                    f"[MULTI GRAB] touch id={id(touch)} holders={holders} active={_name_of(self)}"
                )
            # Always log at least once per (sv, touch) when active
            printed_key = f"dbg_move_logged_{getattr(self, 'uid', id(self))}"
            if not touch.ud.get(printed_key):
                holders = [
                    _name_of(w()) for w in gl if callable(w) and w() is not None
                ]
                current = getattr(touch, "grab_current", None)
                current_name = _name_of(current) if current else "None"
                print(
                    f"[MOVE ACTIVE] {_name_of(self)} grabbed={is_grabbed} grab_current={current_name} "
                    f"holders={holders} touch id={id(touch)}"
                )
                touch.ud[printed_key] = True
            if not is_grabbed:
                holders = [
                    _name_of(w()) for w in gl if callable(w) and w() is not None
                ]
                current = getattr(touch, "grab_current", None)
                current_name = _name_of(current) if current else "None"
                print(
                    f"[GRAB MISMATCH] {_name_of(self)} has self._touch but is not in grab_list | "
                    f"grab_current={current_name} holders={holders} touch id={id(touch)}"
                )
    except Exception:
        # Never let debug code break input handling
        pass
    return _orig_move(self, touch)


ScrollView.on_touch_move = _debug_on_touch_move


@wraps(_orig_down)
def _debug_on_touch_down(self, touch):
    try:
        # Pre-call diagnostics: where did this down land relative to this SV?
        collides = False
        try:
            collides = self.collide_point(*getattr(touch, 'pos', (None, None)))
        except Exception:
            pass
        print(
            f"[DOWN SEEN] {_name_of(self)} pos={getattr(touch,'pos',None)} bbox=(x={self.x}, y={self.y}, w={self.width}, h={self.height}) collide={collides}"
        )
        # Let original decide first if we start handling this touch
        handled = _orig_down(self, touch)
        if handled:
            gl = getattr(touch, "grab_list", []) or []
            holders = [
                _name_of(w()) for w in gl if callable(w) and w() is not None
            ]
            current = getattr(touch, "grab_current", None)
            current_name = _name_of(current) if current else "None"
            print(
                f"[DOWN HANDLED] {_name_of(self)} grabbed={any(w() is self for w in gl)} "
                f"grab_current={current_name} holders={holders} touch id={id(touch)}"
            )
        return handled
    except Exception:
        return _orig_down(self, touch)


ScrollView.on_touch_down = _debug_on_touch_down


@wraps(_orig_change_mode)
def _debug_change_touch_mode(self, *largs):
    try:
        t = getattr(self, "_touch", None)
        tid = id(t) if t is not None else None
        print(f"[_change_touch_mode] {_name_of(self)} starting with _touch id={tid}")
    except Exception:
        pass
    return _orig_change_mode(self, *largs)


@wraps(_orig_sim_down)
def _debug_simulate_touch_down(self, touch):
    try:
        print(f"[simulate_touch_down] {_name_of(self)} re-dispatch touch id={id(touch)}")
    except Exception:
        pass
    return _orig_sim_down(self, touch)


ScrollView._change_touch_mode = _debug_change_touch_mode
ScrollView.simulate_touch_down = _debug_simulate_touch_down


@wraps(_orig_up)
def _debug_on_touch_up(self, touch):
    try:
        gl = getattr(touch, "grab_list", []) or []
        holders = [
            _name_of(w()) for w in gl if callable(w) and w() is not None
        ]
        print(
            f"[UP CALL] {_name_of(self)} holders_before={holders} grab_current={_name_of(getattr(touch, 'grab_current', None)) if getattr(touch, 'grab_current', None) else 'None'} touch id={id(touch)}"
        )
    except Exception:
        pass
    handled = _orig_up(self, touch)
    try:
        gl = getattr(touch, "grab_list", []) or []
        holders_after = [
            _name_of(w()) for w in gl if callable(w) and w() is not None
        ]
        print(
            f"[UP RETURN] {_name_of(self)} handled={handled} holders_after={holders_after} touch id={id(touch)}"
        )
    except Exception:
        pass
    return handled


ScrollView.on_touch_up = _debug_on_touch_up


# Window-level event logging to correlate actual downs/moves/ups and touch ids
def _win_down(win, touch):
    print(f"[WINDOW DOWN] touch id={id(touch)} pos={getattr(touch,'pos',None)} button={getattr(touch,'button',None)}")
    return False


def _win_move(win, touch):
    # Keep verbose output manageable: only log every Nth move per touch
    key = f"win_move_logged_{id(touch)}"
    if not getattr(touch, key, False):
        print(f"[WINDOW MOVE] touch id={id(touch)} pos={getattr(touch,'pos',None)}")
        setattr(touch, key, True)
    return False


def _win_up(win, touch):
    print(f"[WINDOW UP] touch id={id(touch)} pos={getattr(touch,'pos',None)} button={getattr(touch,'button',None)}")
    return False


Window.bind(on_touch_down=_win_down, on_touch_move=_win_move, on_touch_up=_win_up)


class NestedScrollViewTest(App):
    def build(self):
        
        # Main horizontal layout
        main_layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        
        # Left side: Vertical ScrollView with horizontal ScrollViews inside
        left_vertical_sv = ScrollView(
            do_scroll_x=False,  # Only vertical scrolling
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 0.6, 1.0, 0.8]
        )
        left_vertical_sv._debug_name = "left-vertical"
        
        # Container for horizontal ScrollViews
        left_container = BoxLayout(
            orientation='vertical',
            spacing='20dp',
            size_hint_y=None
        )
        left_container.bind(minimum_height=left_container.setter('height'))
        
        # Add multiple horizontal ScrollViews
        for i in range(8):
            # Create a horizontal ScrollView
            horizontal_sv = ScrollView(
                do_scroll_x=True,   # Only horizontal scrolling
                do_scroll_y=False,
                scroll_type=['bars', 'content'],
                size_hint_y=None,
                height=dp(120),
                bar_width=dp(6),
                bar_color=[1.0, 0.5, 0.3, 0.8]
            )
            horizontal_sv._debug_name = f"left-row-{i+1}-horizontal"
            
            # Create content for horizontal ScrollView
            horizontal_content = BoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_x=None
            )
            horizontal_content.bind(minimum_width=horizontal_content.setter('width'))
            
            # Add a label to identify this row
            label = Label(
                text=f'Row {i+1} - Horizontal Scroll',
                size_hint_x=None,
                width=dp(200),
                height=dp(30),
                color=[1, 1, 1, 1],
                bold=True
            )
            horizontal_content.add_widget(label)
            
            # Add buttons to make content wider than the ScrollView
            for j in range(15):
                btn = Button(
                    text=f'Btn {j+1}',
                    size_hint_x=None,
                    width=dp(100),
                    height=dp(80),
                    background_color=[0.2 + (i * 0.1) % 0.8, 0.3, 0.7, 1]
                )
                horizontal_content.add_widget(btn)
            
            horizontal_sv.add_widget(horizontal_content)
            left_container.add_widget(horizontal_sv)
        
        left_vertical_sv.add_widget(left_container)
        
        # Right side: Horizontal ScrollView with vertical ScrollViews inside
        right_horizontal_sv = ScrollView(
            do_scroll_x=True,   # Only horizontal scrolling
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=[0.3, 1.0, 0.6, 0.8]
        )
        right_horizontal_sv._debug_name = "right-horizontal"
        
        # Container for vertical ScrollViews
        right_container = BoxLayout(
            orientation='horizontal',
            spacing='20dp',
            size_hint_x=None
        )
        right_container.bind(minimum_width=right_container.setter('width'))
        
        # Add multiple vertical ScrollViews
        for i in range(6):
            # Create a vertical ScrollView
            vertical_sv = ScrollView(
                do_scroll_x=False,  # Only vertical scrolling
                do_scroll_y=True,
                scroll_type=['bars', 'content'],
                size_hint_x=None,
                width=dp(200),
                bar_width=dp(6),
                bar_color=[1.0, 0.3, 0.5, 0.8]
            )
            vertical_sv._debug_name = f"right-col-{i+1}-vertical"
            
            # Create content for vertical ScrollView
            vertical_content = GridLayout(
                cols=1,
                spacing=dp(10),
                size_hint_y=None,
                height=0
            )
            vertical_content.bind(minimum_height=vertical_content.setter('height'))
            
            # Add a label to identify this column
            label = Label(
                text=f'Column {i+1}\nVertical Scroll',
                size_hint_y=None,
                height=dp(40),
                color=[1, 1, 1, 1],
                bold=True
            )
            vertical_content.add_widget(label)
            
            # Add buttons to make content taller than the ScrollView
            for j in range(20):
                btn = Button(
                    text=f'Item {j+1}',
                    size_hint_y=None,
                    height=dp(60),
                    background_color=[0.7, 0.3, 0.2 + (i * 0.1) % 0.8, 1]
                )
                vertical_content.add_widget(btn)
            
            vertical_sv.add_widget(vertical_content)
            right_container.add_widget(vertical_sv)
        
        right_horizontal_sv.add_widget(right_container)
        
        # Add both sides to main layout
        main_layout.add_widget(left_vertical_sv)
        main_layout.add_widget(right_horizontal_sv)
        
        return main_layout


if __name__ == '__main__':
    NestedScrollViewTest().run()
