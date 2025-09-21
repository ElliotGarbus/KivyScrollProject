from kivy.clock import Clock
from kivy.effects.dampedscroll import DampedScrollEffect
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty
from kivy.uix.stencilview import StencilView

from gesture_recognizer import GestureRecognizer


class GestureScrollView(StencilView):
    """ScrollView variant that delegates gesture recognition to GestureRecognizer.

    Public events remain the same: on_scroll_start/on_scroll_move/on_scroll_stop.
    """

    scroll_distance = NumericProperty('20sp')
    scroll_timeout = NumericProperty(250)
    scroll_wheel_distance = NumericProperty('20sp')

    scroll_x = NumericProperty(0.)
    scroll_y = NumericProperty(1.)

    do_scroll_x = BooleanProperty(True)
    do_scroll_y = BooleanProperty(True)

    effect_cls = ObjectProperty(DampedScrollEffect, allownone=True)
    effect_x = ObjectProperty(None, allownone=True)
    effect_y = ObjectProperty(None, allownone=True)

    smooth_scroll_end = NumericProperty(None, allownone=True)

    __events__ = ('on_scroll_start', 'on_scroll_move', 'on_scroll_stop')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._viewport = None
        # Effects
        if self.effect_x is None and self.effect_cls:
            self.effect_x = self.effect_cls()
        if self.effect_y is None and self.effect_cls:
            self.effect_y = self.effect_cls()

        # Recognizer wiring
        self._recognizer = GestureRecognizer(
            owner=self,
            uid_provider=lambda: str(id(self)),
            get_props=self._get_props,
            request_grab=self._request_grab,
            request_ungrab=self._request_ungrab,
            apply_content_drag=self._apply_content_drag,
            stop_content_at=self._stop_content_at,
            apply_bar_drag=self._apply_bar_drag,
        )
        self._recognizer.bind(
            on_scroll_start=self._on_recognizer_start,
            on_scroll_move=self._on_recognizer_move,
            on_scroll_stop=self._on_recognizer_stop,
            on_pending_timeout=self._on_pending_timeout,
        )
        # Keep content positioned when size or scroll values change
        self.bind(scroll_x=lambda *_: self.update_from_scroll(),
                  scroll_y=lambda *_: self.update_from_scroll())
        self.fbind('size', lambda *_: self.update_from_scroll())

    # ----- Recognizer integration helpers -----
    def _get_props(self):
        return {
            'do_scroll_x': self.do_scroll_x,
            'do_scroll_y': self.do_scroll_y,
            # Kivy properties already resolve 'sp' values; pass through
            'scroll_distance': float(self.scroll_distance),
            'scroll_timeout': int(self.scroll_timeout),
            'smooth_scroll_end': self.smooth_scroll_end,
            'scroll_wheel_distance': float(self.scroll_wheel_distance),
        }

    def _request_grab(self, touch):
        touch.grab(self)

    def _request_ungrab(self, touch):
        try:
            touch.ungrab(self)
        except Exception:
            pass

    def _apply_content_drag(self, dx, dy):
        # Absolute mapping based on initial anchor -> prevents drift.
        vp = self._viewport
        if not vp:
            return
        touch = self._recognizer._active_touch
        if not touch:
            return
        anchor = getattr(self, '_drag_anchor', None) or {}
        if self.do_scroll_x:
            overflow_x = float(max(vp.width - self.width, 0))
            if overflow_x:
                delta_x = float(touch.x) - float(anchor.get('anchor_x', touch.x))
                start_scroll_x = float(anchor.get('start_scroll_x', self.scroll_x))
                new_x = start_scroll_x - (delta_x / overflow_x)
                self.scroll_x = 0.0 if new_x < 0.0 else 1.0 if new_x > 1.0 else new_x
        if self.do_scroll_y:
            overflow_y = float(max(vp.height - self.height, 0))
            if overflow_y:
                delta_y = float(touch.y) - float(anchor.get('anchor_y', touch.y))
                start_scroll_y = float(anchor.get('start_scroll_y', self.scroll_y))
                new_y = start_scroll_y + (delta_y / overflow_y)
                self.scroll_y = 0.0 if new_y < 0.0 else 1.0 if new_y > 1.0 else new_y
        self.update_from_scroll()

    def _stop_content_at(self, x, y):
        if self.effect_x:
            self.effect_x.stop(x)
        if self.effect_y:
            self.effect_y.stop(y)

    def _apply_bar_drag(self, dx, dy):
        # For bar source, owner computes the proper fraction; placeholder here
        if self.do_scroll_x:
            self.scroll_x = min(max(self.scroll_x + dx, 0.), 1.)
        if self.do_scroll_y:
            self.scroll_y = min(max(self.scroll_y + dy, 0.), 1.)
        self.update_from_scroll()

    # ----- Public events -----
    def on_scroll_start(self, touch):
        pass

    def on_scroll_move(self, touch):
        pass

    def on_scroll_stop(self, touch):
        pass

    # ----- Kivy input delegation -----
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        # Bar-hit detection is left as a future refinement; treat as content for now
        touch.push()
        try:
            touch.apply_transform_2d(self.to_local)
            # Recognizer should see the touch before children so it can enter
            # pending mode and later re-dispatch on timeout like updated_sv.
            if self._recognizer.handle_touch_down(touch, source='content'):
                return True
        finally:
            touch.pop()
        # If recognizer didn't take it immediately (e.g., out of bounds), offer to children
        touch.push()
        try:
            touch.apply_transform_2d(self.to_local)
            return super().on_touch_down(touch)
        finally:
            touch.pop()

    def on_touch_move(self, touch):
        touch.push()
        try:
            touch.apply_transform_2d(self.to_local)
            if self._recognizer.handle_touch_move(touch):
                return True
        finally:
            touch.pop()
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        touch.push()
        try:
            touch.apply_transform_2d(self.to_local)
            if self._recognizer.handle_touch_up(touch):
                return True
        finally:
            touch.pop()
        return super().on_touch_up(touch)

    # ----- Recognizer callback -----
    def _on_recognizer_start(self, _recognizer, touch):
        # Record anchor for absolute mapping
        if touch is not None:
            self._drag_anchor = {
                'anchor_x': float(touch.x),
                'anchor_y': float(touch.y),
                'start_scroll_x': float(self.scroll_x),
                'start_scroll_y': float(self.scroll_y),
            }
        self.dispatch('on_scroll_start', touch)

    def _on_recognizer_move(self, _recognizer, touch):
        self.dispatch('on_scroll_move', touch)

    def _on_recognizer_stop(self, _recognizer, touch):
        self.dispatch('on_scroll_stop', touch)
        if hasattr(self, '_drag_anchor'):
            delattr(self, '_drag_anchor')

    def _on_pending_timeout(self, _recognizer, touch):
        # Timeout without scroll → bubble to children by re-dispatching
        touch.push()
        try:
            touch.apply_transform_2d(self.to_local)
            super().on_touch_down(touch)
        finally:
            touch.pop()

    # ----- Child management and layout -----
    def add_widget(self, widget, index=0, canvas=None):
        if self._viewport is None:
            self._viewport = widget
            super().add_widget(widget, index=index, canvas=canvas)
            # Keep content positioned when child size changes
            widget.fbind('size', lambda *_: self.update_from_scroll())
            Clock.schedule_once(lambda _dt: self.update_from_scroll(), 0)
            return
        # Only a single child is supported for this minimal demo
        return super().add_widget(widget, index=index, canvas=canvas)

    def update_from_scroll(self):
        vp = self._viewport
        if not vp:
            return
        # Position child relative to scroll values; child coords are relative to parent
        max_x = max(vp.width - self.width, 0)
        max_y = max(vp.height - self.height, 0)
        # Child coordinates are relative to this widget; do not add self.x/y
        vp.x = - float(self.scroll_x) * max_x
        # scroll_y=1 => top aligned (y=0); scroll_y=0 => bottom aligned (y=-(max_y))
        vp.y = - (1.0 - float(self.scroll_y)) * max_y


