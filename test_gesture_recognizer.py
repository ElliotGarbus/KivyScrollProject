import sys
import types
import time

# Create minimal fake Kivy modules so tests can run without real Kivy
kivy = types.ModuleType('kivy')
kivy.clock = types.ModuleType('kivy.clock')
kivy.config = types.ModuleType('kivy.config')
kivy.event = types.ModuleType('kivy.event')


class _DummyClock:
    frames = 0

    @staticmethod
    def get_time():
        return time.time()

    @staticmethod
    def get_boottime():
        return time.time()

    @staticmethod
    def schedule_once(callback, timeout_s):
        # Return a cancellable object; tests may manually invoke callbacks.
        class _Evt:
            def cancel(self_inner):
                pass

        return _Evt()


class _DummyConfig:
    @staticmethod
    def getint(section, key):
        defaults = {('widgets', 'scroll_timeout'): 250, ('widgets', 'scroll_distance'): 20}
        return defaults.get((section, key), 0)


class _EventDispatcher:
    __events__ = ()

    def __init__(self, **kwargs):
        self._bindings = {}

    def bind(self, **kwargs):
        self._bindings.update(kwargs)

    def dispatch(self, event, *args, **kwargs):
        cb = self._bindings.get(event)
        if cb:
            cb(self, *args)


kivy.clock.Clock = _DummyClock
kivy.config.Config = _DummyConfig
kivy.event.EventDispatcher = _EventDispatcher

sys.modules['kivy'] = kivy
sys.modules['kivy.clock'] = kivy.clock
sys.modules['kivy.config'] = kivy.config
sys.modules['kivy.event'] = kivy.event

from gesture_recognizer import GestureRecognizer


class DummyTouch:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.dx = 0.0
        self.dy = 0.0
        self.pos = (x, y)
        self.ud = {}
        self._grabbed = set()

    def grab(self, widget):
        self._grabbed.add(widget)

    def ungrab(self, widget):
        self._grabbed.discard(widget)


class DummyOwner:
    def __init__(self):
        self.do_scroll_x = True
        self.do_scroll_y = True
        self.scroll_distance = 10
        self.scroll_timeout = 50
        self.smooth_scroll_end = None
        self.scroll_wheel_distance = 20
        self.dragged = []
        self.grabbed = False
        self.ungrabbed = False
        self.events = []

    def get_props(self):
        return {
            'do_scroll_x': self.do_scroll_x,
            'do_scroll_y': self.do_scroll_y,
            'scroll_distance': self.scroll_distance,
            'scroll_timeout': self.scroll_timeout,
            'smooth_scroll_end': self.smooth_scroll_end,
            'scroll_wheel_distance': self.scroll_wheel_distance,
        }

    def request_grab(self, touch):
        self.grabbed = True
        touch.grab(self)

    def request_ungrab(self, touch):
        self.ungrabbed = True
        touch.ungrab(self)

    def apply_content_drag(self, dx, dy):
        self.dragged.append((dx, dy))

    def stop_content_at(self, x, y):
        pass

    def apply_bar_drag(self, dx, dy):
        self.dragged.append((dx, dy))


def _mk_rec(owner: DummyOwner) -> GestureRecognizer:
    rec = GestureRecognizer(
        owner=owner,
        uid_provider=lambda: 'test',
        get_props=owner.get_props,
        request_grab=owner.request_grab,
        request_ungrab=owner.request_ungrab,
        apply_content_drag=owner.apply_content_drag,
        stop_content_at=owner.stop_content_at,
        apply_bar_drag=owner.apply_bar_drag,
    )
    rec.bind(
        on_scroll_start=lambda *_: owner.events.append('start'),
        on_scroll_move=lambda *_: owner.events.append('move'),
        on_scroll_stop=lambda *_: owner.events.append('stop'),
        on_pending_timeout=lambda *_: owner.events.append('timeout'),
    )
    return rec


def test_pending_timeout_yields():
    owner = DummyOwner()
    rec = _mk_rec(owner)
    t = DummyTouch()
    # Down enters pending, consumed
    assert rec.handle_touch_down(t, source='content') is True
    # Wait past timeout
    time.sleep((owner.scroll_timeout + 10) / 1000.0)
    # Let Kivy Clock tick; here we directly invoke the internal timeout
    rec._on_pending_timeout(0)
    assert 'timeout' in owner.events


def test_threshold_cross_starts_scroll():
    owner = DummyOwner()
    rec = _mk_rec(owner)
    t = DummyTouch()
    assert rec.handle_touch_down(t, source='content') is True
    # Simulate moves under threshold
    for _ in range(3):
        t.dx, t.dy = 2, 1
        assert rec.handle_touch_move(t) in (False, True)
    # Cross threshold
    t.dx, t.dy = 20, 0
    assert rec.handle_touch_move(t) is True
    assert 'start' in owner.events
    assert 'move' in owner.events


def test_disabled_axis_yield():
    owner = DummyOwner()
    owner.do_scroll_x = False
    owner.do_scroll_y = True
    rec = _mk_rec(owner)
    t = DummyTouch()
    assert rec.handle_touch_down(t, source='content') is True
    # Move mostly in X beyond threshold → should yield (False)
    t.dx, t.dy = owner.scroll_distance + 5, 0
    assert rec.handle_touch_move(t) is False


def test_single_touch_policy():
    owner = DummyOwner()
    rec = _mk_rec(owner)
    t1 = DummyTouch()
    t2 = DummyTouch()
    assert rec.handle_touch_down(t1, source='content') is True
    # Second touch should not be taken
    assert rec.handle_touch_down(t2, source='content') is False
    # End first touch
    rec.handle_touch_up(t1)
    assert 'stop' in owner.events


def test_wheel_generates_moves():
    owner = DummyOwner()
    rec = _mk_rec(owner)
    assert rec.handle_wheel(0, -owner.scroll_wheel_distance) is True
    assert 'start' in owner.events
    assert 'move' in owner.events
    assert 'stop' in owner.events


def test_bar_source_immediate_scroll():
    owner = DummyOwner()
    rec = _mk_rec(owner)
    t = DummyTouch()
    # Bar source should start scrolling immediately (no pending)
    assert rec.handle_touch_down(t, source='bar') is True
    assert 'start' in owner.events
    # Move should apply drag and emit move
    t.dx, t.dy = 5, -3
    assert rec.handle_touch_move(t) is True
    assert owner.dragged[-1] == (5, -3)
    assert 'move' in owner.events
    # Up should stop
    assert rec.handle_touch_up(t) is True
    assert 'stop' in owner.events


def test_axis_lock_set_on_threshold_cross():
    owner = DummyOwner()
    rec = _mk_rec(owner)
    t = DummyTouch()
    assert rec.handle_touch_down(t, source='content') is True
    # Accumulate small motion
    for _ in range(2):
        t.dx, t.dy = 3, 1
        rec.handle_touch_move(t)
    # Cross threshold with dominant x
    t.dx, t.dy = owner.scroll_distance + 1, 0
    rec.handle_touch_move(t)
    info = rec.get_event_info(t)
    # Axis lock should be 'x' when both axes allowed and x dominates
    assert info.get('axis_lock') in ('x', 'both', None)
    # If both axes active, expect 'x'
    if owner.do_scroll_x and owner.do_scroll_y:
        assert info.get('axis_lock') == 'x'


