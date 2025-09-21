from typing import Callable, Dict, Optional, Tuple, Any

from kivy.clock import Clock
from kivy.config import Config
from kivy.event import EventDispatcher


class GestureRecognizer(EventDispatcher):
    """Generic gesture recognizer focused on ScrollView needs (pan/scroll + wheel).

    This recognizer is single-touch for scrolling: it tracks at most one
    active touch at a time. Additional simultaneous touches are ignored
    (returned as unhandled) so they may bubble to child widgets.

    Events emitted (owner mirrors to ScrollView's public events):
        - on_scroll_start(touch)
        - on_scroll_move(touch)
        - on_scroll_stop(touch)

    The recognizer stores its per-touch state in `touch.ud['gr.<uid>']`.
    """

    __events__ = (
        'on_scroll_start',
        'on_scroll_move',
        'on_scroll_stop',
        'on_pending_timeout',
    )

    def __init__(
        self,
        owner: Any,
        uid_provider: Optional[Callable[[], str]] = None,
        get_props: Optional[Callable[[], Dict[str, Any]]] = None,
        request_grab: Optional[Callable[[Any], None]] = None,
        request_ungrab: Optional[Callable[[Any], None]] = None,
        apply_content_drag: Optional[Callable[[float, float], None]] = None,
        stop_content_at: Optional[Callable[[float, float], None]] = None,
        apply_bar_drag: Optional[Callable[[float, float], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.owner = owner
        self._uid_provider = uid_provider or (lambda: f'{id(self)}')
        # Recognizer namespace key: 'gr.<uid>'
        self._gr_uid: str = f"gr.{self._uid_provider()}"

        # Owner capability/query hooks
        self._get_props = get_props or self._default_get_props
        self._request_grab = request_grab or (lambda touch: None)
        self._request_ungrab = request_ungrab or (lambda touch: None)
        self._apply_content_drag = apply_content_drag or (lambda dx, dy: None)
        self._stop_content_at = stop_content_at or (lambda x, y: None)
        self._apply_bar_drag = apply_bar_drag or (lambda dx, dy: None)

        # Single active touch being tracked by this recognizer
        self._active_touch: Optional[Any] = None
        self._timeout_ev = None  # type: Optional[Any]

    # ---------------------------
    # Public API
    # ---------------------------
    def handle_touch_down(self, touch: Any, source: str = 'content') -> bool:
        """Process touch down.

        Returns True if consumed by the recognizer (owner should stop
        propagation), else False to allow bubbling.
        """
        if not getattr(touch, 'ud', None) is not None:
            return False

        if self._active_touch is not None:
            # Single-touch policy: do not take additional touches.
            return False

        # Initialize per-touch state
        ud = self._ensure_gr_ud(touch)
        ud['mode'] = 'pending' if source == 'content' else 'scroll'
        ud['source'] = source
        ud['last_x'] = float(getattr(touch, 'x', 0.0) or 0.0)
        ud['last_y'] = float(getattr(touch, 'y', 0.0) or 0.0)
        ud['dx_total'] = 0.0
        ud['dy_total'] = 0.0
        ud['dx_last'] = 0.0
        ud['dy_last'] = 0.0
        ud['velocity'] = None
        ud['frames_start'] = Clock.frames
        ud['timestamp_start'] = Clock.get_time()
        ud['timestamp_last'] = ud['timestamp_start']
        ud['user_stopped'] = False
        ud['axis_lock'] = None

        self._active_touch = touch

        props = self._get_props()
        if source == 'content':
            # Delay grabbing/decision until threshold or timeout
            timeout_s = float(props.get('scroll_timeout', self._read_cfg_timeout())) / 1000.0
            self._schedule_timeout(timeout_s)
            # Consume for now; if timeout fires, we'll notify owner via
            # on_pending_timeout so it can re-dispatch to children.
            return True

        # Bar or wheel start scroll immediately
        self._request_grab(touch)
        self.dispatch('on_scroll_start', touch)
        return True

    def handle_touch_move(self, touch: Any) -> bool:
        if touch is not self._active_touch:
            return False

        ud = self._get_gr_ud(touch)
        if ud is None:
            return False

        props = self._get_props()
        do_scroll_x = bool(props.get('do_scroll_x', True))
        do_scroll_y = bool(props.get('do_scroll_y', True))
        threshold = float(props.get('scroll_distance', self._read_cfg_distance()))

        # Compute local-space deltas from last recorded local position.
        last_x = float(ud.get('last_x', getattr(touch, 'x', 0.0)) or 0.0)
        last_y = float(ud.get('last_y', getattr(touch, 'y', 0.0)) or 0.0)
        curr_x = float(getattr(touch, 'x', 0.0) or 0.0)
        curr_y = float(getattr(touch, 'y', 0.0) or 0.0)
        dx = curr_x - last_x
        dy = curr_y - last_y
        if dx == 0.0 and hasattr(touch, 'dx'):
            dx = float(getattr(touch, 'dx', 0.0) or 0.0)
        if dy == 0.0 and hasattr(touch, 'dy'):
            dy = float(getattr(touch, 'dy', 0.0) or 0.0)
        ud['last_x'] = curr_x
        ud['last_y'] = curr_y
        ud['dx_total'] += abs(dx)
        ud['dy_total'] += abs(dy)
        ud['dx_last'] = dx
        ud['dy_last'] = dy
        ud['timestamp_last'] = Clock.get_time()

        if ud['mode'] == 'pending':
            # Yield immediately to parent if movement exceeds threshold on a
            # disabled axis (nested SV rule).
            if ud['dx_total'] > threshold and not do_scroll_x:
                ud['yield_parent'] = True
                self._clear_active_touch()
                return False
            if ud['dy_total'] > threshold and not do_scroll_y:
                ud['yield_parent'] = True
                self._clear_active_touch()
                return False

            if ((ud['dx_total'] > threshold and do_scroll_x) or
                    (ud['dy_total'] > threshold and do_scroll_y)):
                # Start scrolling precisely from the position where threshold was exceeded.
                # Adjust anchor so there's no visible lag compared to original ScrollView.
                if hasattr(self.owner, '_drag_anchor') and self.owner._drag_anchor:
                    # recompute anchor to the current move frame
                    self.owner._drag_anchor['anchor_x'] = float(touch.x)
                    self.owner._drag_anchor['anchor_y'] = float(touch.y)
                    self.owner._drag_anchor['start_scroll_x'] = float(getattr(self.owner, 'scroll_x', 0.0))
                    self.owner._drag_anchor['start_scroll_y'] = float(getattr(self.owner, 'scroll_y', 1.0))

                ud['mode'] = 'scroll'
                # Lock axis based on dominant movement at time of decision
                if do_scroll_x and do_scroll_y:
                    ud['axis_lock'] = self._compute_axis_lock(ud)
                elif do_scroll_x:
                    ud['axis_lock'] = 'x'
                elif do_scroll_y:
                    ud['axis_lock'] = 'y'
                # Start scrolling: take grab and emit start
                self._cancel_timeout()
                self._request_grab(touch)
                self.dispatch('on_scroll_start', touch)
                # Fall-through to process first move as scroll

        if ud['mode'] != 'scroll':
            return False

        # Apply movement and dispatch events
        if ud['source'] == 'bar':
            self._apply_bar_drag(dx, dy)
            self.dispatch('on_scroll_move', touch)
            return True  # Consume bar touches
        else:
            # For content touches, just dispatch the event but let ScrollView handle the drag
            self.dispatch('on_scroll_move', touch)
            return False  # Don't consume content touches

    def handle_touch_up(self, touch: Any) -> bool:
        if touch is not self._active_touch:
            return False

        ud = self._get_gr_ud(touch)
        if ud is None:
            self._clear_active_touch()
            return False

        self._cancel_timeout()

        # Compute a simple per-axis instantaneous velocity from last frame
        dt = max(Clock.get_boottime() - (ud.get('timestamp_last') or Clock.get_time()), 1e-6)
        vx = (ud['dx_last'] / dt) if dt else 0.0
        vy = (ud['dy_last'] / dt) if dt else 0.0
        ud['velocity'] = (vx, vy)
        ud['mode'] = 'stopped'

        self.dispatch('on_scroll_stop', touch)
        self._request_ungrab(touch)
        self._clear_active_touch()
        return True

    def handle_wheel(self, delta_x: float, delta_y: float, pos: Optional[Tuple[float, float]] = None) -> bool:
        """Process a wheel input as scroll deltas.

        The owner is responsible for routing wheel events here with the same
        sign convention currently used by ScrollView.
        """
        props = self._get_props()
        do_scroll_x = bool(props.get('do_scroll_x', True))
        do_scroll_y = bool(props.get('do_scroll_y', True))
        
        # Only handle if scrolling is enabled on at least one axis that has movement
        if not ((do_scroll_x and delta_x != 0.0) or (do_scroll_y and delta_y != 0.0)):
            return False
            
        # Create a synthetic touch-like object for wheel events
        class WheelTouch:
            def __init__(self, x=0.0, y=0.0):
                self.x = x
                self.y = y
                self.dx = delta_x
                self.dy = delta_y
                self.pos = (x, y)
                self.ud = {self._gr_uid: {
                    'mode': 'scroll',
                    'source': 'wheel',
                    'dx_total': abs(delta_x),
                    'dy_total': abs(delta_y),
                    'dx_last': delta_x,
                    'dy_last': delta_y,
                    'velocity': None,
                    'frames_start': 0,
                    'timestamp_start': 0,
                    'timestamp_last': 0,
                    'user_stopped': False,
                    'axis_lock': None,
                }}
        
        if pos:
            wheel_touch = WheelTouch(pos[0], pos[1])
        else:
            wheel_touch = WheelTouch()
            
        # Emit scroll events for wheel
        self.dispatch('on_scroll_start', wheel_touch)
        self._apply_content_drag(float(delta_x), float(delta_y))
        self.dispatch('on_scroll_move', wheel_touch)
        self.dispatch('on_scroll_stop', wheel_touch)
        return True

    def cancel_current_gesture(self) -> None:
        if not self._active_touch:
            return
        touch = self._active_touch
        self._cancel_timeout()
        self._request_ungrab(touch)
        self._clear_active_touch()

    def get_event_info(self, touch: Any) -> Dict[str, Any]:
        ud = self._get_gr_ud(touch)
        return dict(ud) if ud else {}

    # ---------------------------
    # Event stubs
    # ---------------------------
    def on_scroll_start(self, touch: Any) -> None:
        pass

    def on_scroll_move(self, touch: Any) -> None:
        pass

    def on_scroll_stop(self, touch: Any) -> None:
        pass

    def on_pending_timeout(self, touch: Any) -> None:
        pass

    # ---------------------------
    # Internals
    # ---------------------------
    def _default_get_props(self) -> Dict[str, Any]:
        """Fallback props using Kivy Config; owner can override via get_props()."""
        try:
            timeout_ms = Config.getint('widgets', 'scroll_timeout')
        except Exception:
            timeout_ms = 250
        try:
            distance = Config.getint('widgets', 'scroll_distance')
        except Exception:
            distance = 20
        props = {
            'do_scroll_x': True,
            'do_scroll_y': True,
            'scroll_timeout': timeout_ms,
            'scroll_distance': distance,
            'smooth_scroll_end': None,
            'scroll_wheel_distance': 20,
        }
        # If owner has attributes, prefer them
        for key in list(props.keys()):
            if hasattr(self.owner, key):
                props[key] = getattr(self.owner, key)
        return props

    def _read_cfg_timeout(self) -> int:
        try:
            return Config.getint('widgets', 'scroll_timeout')
        except Exception:
            return 250

    def _read_cfg_distance(self) -> float:
        try:
            return float(Config.getint('widgets', 'scroll_distance'))
        except Exception:
            return 20.0

    def _ensure_gr_ud(self, touch: Any) -> Dict[str, Any]:
        ud = getattr(touch, 'ud', None)
        if ud is None:
            touch.ud = {}
            ud = touch.ud
        if self._gr_uid not in ud:
            ud[self._gr_uid] = {}
        return ud[self._gr_uid]

    def _get_gr_ud(self, touch: Any) -> Optional[Dict[str, Any]]:
        ud = getattr(touch, 'ud', None)
        if not ud:
            return None
        return ud.get(self._gr_uid)

    def _schedule_timeout(self, timeout_s: float) -> None:
        self._cancel_timeout()
        self._timeout_ev = Clock.schedule_once(self._on_pending_timeout, timeout_s)

    def _cancel_timeout(self) -> None:
        ev = self._timeout_ev
        if ev is not None:
            try:
                ev.cancel()
            except Exception:
                pass
        self._timeout_ev = None

    def _on_pending_timeout(self, _dt: float) -> None:
        # If still pending when timeout fires, do not start scrolling; leave
        # it to the owner to re-dispatch the touch to children.
        touch = self._active_touch
        if not touch:
            return
        ud = self._get_gr_ud(touch)
        if not ud or ud.get('mode') != 'pending':
            return
        # Mark as timed-out by switching to stopped-without-scroll state.
        ud['mode'] = 'stopped'
        # Notify owner so it can simulate child dispatch
        self.dispatch('on_pending_timeout', touch)
        self._request_ungrab(touch)
        self._clear_active_touch()

    def _clear_active_touch(self) -> None:
        self._active_touch = None

    @staticmethod
    def _compute_axis_lock(ud: Dict[str, Any]) -> Optional[str]:
        dx = ud.get('dx_total') or 0.0
        dy = ud.get('dy_total') or 0.0
        if dx == 0 and dy == 0:
            return None
        return 'x' if dx >= dy else 'y'


