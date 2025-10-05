'''
ScrollView
==========

.. versionadded:: 1.0.4

The :class:`ScrollView` widget provides a scrollable/pannable viewport that is
clipped at the scrollview's bounding box.

.. note::
    Use :class:`~kivy.uix.recycleview.RecycleView` for generating large
    numbers of widgets in order to display many data items.


Scrolling Behavior
------------------

The ScrollView accepts only one child and applies a viewport/window to
it according to the :attr:`~ScrollView.scroll_x` and
:attr:`~ScrollView.scroll_y` properties. Touches are analyzed to
determine if the user wants to scroll or control the child in some
other manner: you cannot do both at the same time. To determine if
interaction is a scrolling gesture, these properties are used:

    - :attr:`~ScrollView.scroll_distance`: the minimum distance to travel,
      defaults to 20 pixels.
    - :attr:`~ScrollView.scroll_timeout`: the maximum time period, defaults
      to 55 milliseconds.

If a touch travels :attr:`~ScrollView.scroll_distance` pixels within the
:attr:`~ScrollView.scroll_timeout` period, it is recognized as a scrolling
gesture and translation (scroll/pan) will begin. If the timeout occurs, the
touch down event is dispatched to the child instead (no translation).

The default value for those settings can be changed in the configuration file::

    [widgets]
    scroll_timeout = 250
    scroll_distance = 20

.. versionadded:: 1.1.1

    ScrollView now animates scrolling in Y when a mousewheel is used.


Limiting to the X or Y Axis
---------------------------

By default, the ScrollView allows scrolling along both the X and Y axes. You
can explicitly disable scrolling on an axis by setting the
:attr:`~ScrollView.do_scroll_x` or :attr:`~ScrollView.do_scroll_y` properties
to False.


Managing the Content Size and Position
--------------------------------------

The ScrollView manages the position of its children similarly to a
:class:`~kivy.uix.relativelayout.RelativeLayout` but does not use the
:attr:`~kivy.uix.widget.Widget.size_hint`. You must
carefully specify the :attr:`~kivy.uix.widget.Widget.size` of your content to
get the desired scroll/pan effect.

By default, the :attr:`~kivy.uix.widget.Widget.size_hint` is (1, 1), so the
content size will fit your ScrollView
exactly (you will have nothing to scroll). You must deactivate at least one of
the size_hint instructions (x or y) of the child to enable scrolling.
Setting :attr:`~kivy.uix.widget.Widget.size_hint_min` to not be None will
also enable scrolling for that dimension when the :class:`ScrollView` is
smaller than the minimum size.

To scroll a :class:`~kivy.uix.gridlayout.GridLayout` on it's Y-axis/vertically,
set the child's width  to that of the ScrollView (size_hint_x=1), and set
the size_hint_y property to None::

    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.core.window import Window
    from kivy.app import runTouchApp

    layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
    # Make sure the height is such that there is something to scroll.
    layout.bind(minimum_height=layout.setter('height'))
    for i in range(100):
        btn = Button(text=str(i), size_hint_y=None, height=40)
        layout.add_widget(btn)
    root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
    root.add_widget(layout)

    runTouchApp(root)


Kv Example::

    ScrollView:
        do_scroll_x: False
        do_scroll_y: True

        Label:
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            padding: 10, 10
            text:
                'really some amazing text\\n' * 100

Overscroll Effects
------------------

.. versionadded:: 1.7.0

When scrolling would exceed the bounds of the :class:`ScrollView`, it
uses a :class:`~kivy.effects.scroll.ScrollEffect` to handle the
overscroll. These effects can perform actions like bouncing back,
changing opacity, or simply preventing scrolling beyond the normal
boundaries. Note that complex effects may perform many computations,
which can be slow on weaker hardware.

You can change what effect is being used by setting
:attr:`~ScrollView.effect_cls` to any effect class. Current options
include:

    - :class:`~kivy.effects.scroll.ScrollEffect`: Does not allow
      scrolling beyond the :class:`ScrollView` boundaries.
    - :class:`~kivy.effects.dampedscroll.DampedScrollEffect`: The
      current default. Allows the user to scroll beyond the normal
      boundaries, but has the content spring back once the
      touch/click is released.
    - :class:`~kivy.effects.opacityscroll.OpacityScrollEffect`: Similar
      to the :class:`~kivy.effect.dampedscroll.DampedScrollEffect`, but
      also reduces opacity during overscroll.

You can also create your own scroll effect by subclassing one of these,
then pass it as the :attr:`~ScrollView.effect_cls` in the same way.

Alternatively, you can set :attr:`~ScrollView.effect_x` and/or
:attr:`~ScrollView.effect_y` to an *instance* of the effect you want to
use. This will override the default effect set in
:attr:`~ScrollView.effect_cls`.

All the effects are located in the :mod:`kivy.effects`.

'''

__all__ = ('ScrollView', )

from functools import partial
from kivy.animation import Animation
from kivy.config import Config
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.stencilview import StencilView
from kivy.metrics import dp
from kivy.effects.dampedscroll import DampedScrollEffect
from kivy.properties import NumericProperty, BooleanProperty, AliasProperty, \
    ObjectProperty, ListProperty, ReferenceListProperty, OptionProperty, \
    ColorProperty
from kivy.uix.behaviors import FocusBehavior


# When we are generating documentation, Config doesn't exist
_scroll_timeout = _scroll_distance = 0
if Config:
    _scroll_timeout = Config.getint('widgets', 'scroll_timeout')
    _scroll_distance = '{}sp'.format(Config.getint('widgets',
                                                   'scroll_distance'))


class ScrollView(StencilView):
    '''ScrollView class. See module documentation for more information.

    :Events:
        `on_scroll_start`
            Generic event fired when scrolling starts from touch.
        `on_scroll_move`
            Generic event fired when scrolling move from touch.
        `on_scroll_stop`
            Generic event fired when scrolling stops from touch.

    .. versionchanged:: 1.9.0
        `on_scroll_start`, `on_scroll_move` and `on_scroll_stop` events are
        now dispatched when scrolling to handle nested ScrollViews.

    .. versionchanged:: 1.7.0
        `auto_scroll`, `scroll_friction`, `scroll_moves`, `scroll_stoptime' has
        been deprecated, use :attr:`effect_cls` instead.
    '''

    scroll_distance = NumericProperty(_scroll_distance)
    '''Distance to move before scrolling the :class:`ScrollView`, in pixels. As
    soon as the distance has been traveled, the :class:`ScrollView` will start
    to scroll, and no touch event will go to children.
    It is advisable that you base this value on the dpi of your target device's
    screen.

    :attr:`scroll_distance` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 20 (pixels), according to the default value in user
    configuration.
    '''

    scroll_wheel_distance = NumericProperty('20sp')
    '''Distance to move when scrolling with a mouse wheel.
    It is advisable that you base this value on the dpi of your target device's
    screen.

    .. versionadded:: 1.8.0

    :attr:`scroll_wheel_distance` is a
    :class:`~kivy.properties.NumericProperty` , defaults to 20 pixels.
    '''

    scroll_timeout = NumericProperty(_scroll_timeout)
    '''Timeout allowed to trigger the :attr:`scroll_distance`, in milliseconds.
    If the user has not moved :attr:`scroll_distance` within the timeout,
    the scrolling will be disabled, and the touch event will go to the
    children.

    :attr:`scroll_timeout` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 55 (milliseconds) according to the default value in user
    configuration.

    .. versionchanged:: 1.5.0
        Default value changed from 250 to 55.
    '''

    scroll_x = NumericProperty(0.)
    '''X scrolling value, between 0 and 1. If 0, the content's left side will
    touch the left side of the ScrollView. If 1, the content's right side will
    touch the right side.

    This property is controlled by :class:`ScrollView` only if
    :attr:`do_scroll_x` is True.

    :attr:`scroll_x` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 0.
    '''

    scroll_y = NumericProperty(1.)
    '''Y scrolling value, between 0 and 1. If 0, the content's bottom side will
    touch the bottom side of the ScrollView. If 1, the content's top side will
    touch the top side.

    This property is controlled by :class:`ScrollView` only if
    :attr:`do_scroll_y` is True.

    :attr:`scroll_y` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 1.
    '''

    do_scroll_x = BooleanProperty(True)
    '''Allow scroll on X axis.

    :attr:`do_scroll_x` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True.
    '''

    do_scroll_y = BooleanProperty(True)
    '''Allow scroll on Y axis.

    :attr:`do_scroll_y` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True.
    '''

    def _get_do_scroll(self):
        return (self.do_scroll_x, self.do_scroll_y)

    def _set_do_scroll(self, value):
        if isinstance(value, (list, tuple)):
            self.do_scroll_x, self.do_scroll_y = value
        else:
            self.do_scroll_x = self.do_scroll_y = bool(value)

    do_scroll = AliasProperty(_get_do_scroll, _set_do_scroll,
                              bind=('do_scroll_x', 'do_scroll_y'),
                              cache=True)
    '''Allow scroll on X or Y axis.

    :attr:`do_scroll` is a :class:`~kivy.properties.AliasProperty` of
    (:attr:`do_scroll_x` + :attr:`do_scroll_y`)
    '''

    always_overscroll = BooleanProperty(True)
    '''Make sure user can overscroll even if there is not enough content
    to require scrolling.

    This is useful if you want to trigger some action on overscroll, but
    there is not always enough content to trigger it.

    :attr:`always_overscroll` is a
    :class:`~kivy.properties.BooleanProperty` and defaults to `True`.

    .. versionadded:: 2.0.0

    The option was added and enabled by default, set to False to get the
    previous behavior of only allowing to overscroll when there is
    enough content to allow scrolling.
    '''

    def _get_vbar(self):
        # must return (y, height) in %
        # calculate the viewport size / scrollview size %
        if self._viewport is None:
            return 0, 1.
        vh = self._viewport.height
        h = self.height
        if vh < h or vh == 0:
            return 0, 1.
        ph = max(0.01, h / float(vh))
        sy = min(1.0, max(0.0, self.scroll_y))
        py = (1. - ph) * sy
        return (py, ph)

    vbar = AliasProperty(_get_vbar,
                         bind=('scroll_y', '_viewport', 'viewport_size',
                               'height'),
                         cache=True)
    '''Return a tuple of (position, size) of the vertical scrolling bar.

    .. versionadded:: 1.2.0

    The position and size are normalized between 0-1, and represent a
    proportion of the current scrollview height. This property is used
    internally for drawing the little vertical bar when you're scrolling.

    :attr:`vbar` is a :class:`~kivy.properties.AliasProperty`, readonly.
    '''

    def _get_hbar(self):
        # must return (x, width) in %
        # calculate the viewport size / scrollview size %
        if self._viewport is None:
            return 0, 1.
        vw = self._viewport.width
        w = self.width
        if vw < w or vw == 0:
            return 0, 1.
        pw = max(0.01, w / float(vw))
        sx = min(1.0, max(0.0, self.scroll_x))
        px = (1. - pw) * sx
        return (px, pw)

    hbar = AliasProperty(_get_hbar,
                         bind=('scroll_x', '_viewport', 'viewport_size',
                               'width'),
                         cache=True)
    '''Return a tuple of (position, size) of the horizontal scrolling bar.

    .. versionadded:: 1.2.0

    The position and size are normalized between 0-1, and represent a
    proportion of the current scrollview height. This property is used
    internally for drawing the little horizontal bar when you're scrolling.

    :attr:`hbar` is a :class:`~kivy.properties.AliasProperty`, readonly.
    '''

    bar_color = ColorProperty([.7, .7, .7, .9])
    '''Color of horizontal / vertical scroll bar, in RGBA format.

    .. versionadded:: 1.2.0

    :attr:`bar_color` is a :class:`~kivy.properties.ColorProperty` and defaults
    to [.7, .7, .7, .9].

    .. versionchanged:: 2.0.0
        Changed from :class:`~kivy.properties.ListProperty` to
        :class:`~kivy.properties.ColorProperty`.
    '''

    bar_inactive_color = ColorProperty([.7, .7, .7, .2])
    '''Color of horizontal / vertical scroll bar (in RGBA format), when no
    scroll is happening.

    .. versionadded:: 1.9.0

    :attr:`bar_inactive_color` is a
    :class:`~kivy.properties.ColorProperty` and defaults to [.7, .7, .7, .2].

    .. versionchanged:: 2.0.0
        Changed from :class:`~kivy.properties.ListProperty` to
        :class:`~kivy.properties.ColorProperty`.
    '''

    bar_width = NumericProperty('2dp')
    '''Width of the horizontal / vertical scroll bar. The width is interpreted
    as a height for the horizontal bar.

    .. versionadded:: 1.2.0

    :attr:`bar_width` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 2.
    '''

    bar_pos_x = OptionProperty('bottom', options=('top', 'bottom'))
    '''Which side of the ScrollView the horizontal scroll bar should go
    on. Possible values are 'top' and 'bottom'.

    .. versionadded:: 1.8.0

    :attr:`bar_pos_x` is an :class:`~kivy.properties.OptionProperty`,
    defaults to 'bottom'.

    '''

    bar_pos_y = OptionProperty('right', options=('left', 'right'))
    '''Which side of the ScrollView the vertical scroll bar should go
    on. Possible values are 'left' and 'right'.

    .. versionadded:: 1.8.0

    :attr:`bar_pos_y` is an :class:`~kivy.properties.OptionProperty` and
    defaults to 'right'.

    '''

    bar_pos = ReferenceListProperty(bar_pos_x, bar_pos_y)
    '''Which side of the scroll view to place each of the bars on.

    :attr:`bar_pos` is a :class:`~kivy.properties.ReferenceListProperty` of
    (:attr:`bar_pos_x`, :attr:`bar_pos_y`)
    '''

    bar_margin = NumericProperty(0)
    '''Margin between the bottom / right side of the scrollview when drawing
    the horizontal / vertical scroll bar.

    .. versionadded:: 1.2.0

    :attr:`bar_margin` is a :class:`~kivy.properties.NumericProperty`, default
    to 0
    '''

    effect_cls = ObjectProperty(DampedScrollEffect, allownone=True)
    '''Class effect to instantiate for X and Y axis.

    .. versionadded:: 1.7.0

    :attr:`effect_cls` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to :class:`DampedScrollEffect`.

    .. versionchanged:: 1.8.0
        If you set a string, the :class:`~kivy.factory.Factory` will be used to
        resolve the class.

    '''

    effect_x = ObjectProperty(None, allownone=True)
    '''Effect to apply for the X axis. If None is set, an instance of
    :attr:`effect_cls` will be created.

    .. versionadded:: 1.7.0

    :attr:`effect_x` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None.
    '''

    effect_y = ObjectProperty(None, allownone=True)
    '''Effect to apply for the Y axis. If None is set, an instance of
    :attr:`effect_cls` will be created.

    .. versionadded:: 1.7.0

    :attr:`effect_y` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None, read-only.
    '''

    viewport_size = ListProperty([0, 0])
    '''(internal) Size of the internal viewport. This is the size of your only
    child in the scrollview.
    '''

    scroll_type = OptionProperty(['content'], options=(['content'], ['bars'],
                                 ['bars', 'content'], ['content', 'bars']))
    '''Sets the type of scrolling to use for the content of the scrollview.
    Available options are: ['content'], ['bars'], ['bars', 'content'].

    +---------------------+------------------------------------------------+
    | ['content']         | Content is scrolled by dragging or swiping the |
    |                     | content directly.                              |
    +---------------------+------------------------------------------------+
    | ['bars']            | Content is scrolled by dragging or swiping the |
    |                     | scroll bars.                                   |
    +---------------------+------------------------------------------------+
    | ['bars', 'content'] | Content is scrolled by either of the above     |
    |                     | methods.                                       |
    +---------------------+------------------------------------------------+

    .. versionadded:: 1.8.0

    :attr:`scroll_type` is an :class:`~kivy.properties.OptionProperty` and
    defaults to ['content'].
    '''

    smooth_scroll_end = NumericProperty(None, allownone=True)
    '''Whether smooth scroll end should be used when scrolling with the
    mouse-wheel and the factor of transforming the scroll distance to
    velocity. This option also enables velocity addition meaning if you
    scroll more, you will scroll faster and further. The recommended value
    is `10`. The velocity is calculated as :attr:`scroll_wheel_distance` *
    :attr:`smooth_scroll_end`.

    .. versionadded:: 1.11.0

    :attr:`smooth_scroll_end` is a :class:`~kivy.properties.NumericProperty`
    and defaults to None.
    '''

    # Class constants for mouse wheel scroll button sets
    _MOUSE_WHEEL_HORIZONTAL = {'scrollleft', 'scrollright'}
    _MOUSE_WHEEL_VERTICAL = {'scrolldown', 'scrollup'}
    _MOUSE_WHEEL_DECREASE = {'scrolldown', 'scrollleft'}  # negative direction
    _MOUSE_WHEEL_INCREASE = {'scrollup', 'scrollright'}   # positive direction

    # private, for internal use only

    _viewport = ObjectProperty(None, allownone=True)
    _bar_color = ListProperty([0, 0, 0, 0])
    _effect_x_start_width = None
    _effect_y_start_height = None
    _update_effect_bounds_ev = None
    _bind_inactive_bar_color_ev = None

    def _set_viewport_size(self, instance, value):
        self.viewport_size = value

    def on__viewport(self, instance, value):
        if value:
            value.bind(size=self._set_viewport_size)
            self.viewport_size = value.size

    __events__ = ('on_scroll_start', 'on_scroll_move', 'on_scroll_stop')

    def __init__(self, **kwargs):
        self._touch = None
        self._trigger_update_from_scroll = Clock.create_trigger(
            self.update_from_scroll, -1)
        # create a specific canvas for the viewport
        from kivy.graphics import PushMatrix, Translate, PopMatrix, Canvas
        self.canvas_viewport = Canvas()
        self.canvas = Canvas()
        with self.canvas_viewport.before:
            PushMatrix()
            self.g_translate = Translate(0, 0)
        with self.canvas_viewport.after:
            PopMatrix()

        super(ScrollView, self).__init__(**kwargs)

        self.register_event_type('on_scroll_start')
        self.register_event_type('on_scroll_move')
        self.register_event_type('on_scroll_stop')

        # now add the viewport canvas to our canvas
        self.canvas.add(self.canvas_viewport)

        effect_cls = self.effect_cls
        if isinstance(effect_cls, str):
            effect_cls = Factory.get(effect_cls)
        if self.effect_x is None and effect_cls is not None:
            self.effect_x = effect_cls(target_widget=self._viewport)
        if self.effect_y is None and effect_cls is not None:
            self.effect_y = effect_cls(target_widget=self._viewport)

        trigger_update_from_scroll = self._trigger_update_from_scroll
        update_effect_widget = self._update_effect_widget
        update_effect_x_bounds = self._update_effect_x_bounds
        update_effect_y_bounds = self._update_effect_y_bounds
        fbind = self.fbind
        fbind('width', update_effect_x_bounds)
        fbind('height', update_effect_y_bounds)
        fbind('viewport_size', self._update_effect_bounds)
        fbind('_viewport', update_effect_widget)
        fbind('scroll_x', trigger_update_from_scroll)
        fbind('scroll_y', trigger_update_from_scroll)
        fbind('pos', trigger_update_from_scroll)
        fbind('size', trigger_update_from_scroll)

        trigger_update_from_scroll()
        update_effect_widget()
        update_effect_x_bounds()
        update_effect_y_bounds()

    def on_effect_x(self, instance, value):
        if value:
            value.bind(scroll=self._update_effect_x)
            value.target_widget = self._viewport

    def on_effect_y(self, instance, value):
        if value:
            value.bind(scroll=self._update_effect_y)
            value.target_widget = self._viewport

    def on_effect_cls(self, instance, cls):
        if isinstance(cls, str):
            cls = Factory.get(cls)
        self.effect_x = cls(target_widget=self._viewport)
        self.effect_x.bind(scroll=self._update_effect_x)
        self.effect_y = cls(target_widget=self._viewport)
        self.effect_y.bind(scroll=self._update_effect_y)

    def _update_effect_widget(self, *args):
        if self.effect_x:
            self.effect_x.target_widget = self._viewport
        if self.effect_y:
            self.effect_y.target_widget = self._viewport

    def _update_effect_x_bounds(self, *args):
        if not self._viewport or not self.effect_x:
            return
        scrollable_width = self.width - self.viewport_size[0]
        self.effect_x.min = 0
        self.effect_x.max = min(0, scrollable_width)
        self.effect_x.value = scrollable_width * self.scroll_x

    def _update_effect_y_bounds(self, *args):
        if not self._viewport or not self.effect_y:
            return
        scrollable_height = self.height - self.viewport_size[1]
        self.effect_y.min = 0 if scrollable_height < 0 else scrollable_height
        self.effect_y.max = scrollable_height
        self.effect_y.value = self.effect_y.max * self.scroll_y

    def _update_effect_bounds(self, *args):
        # "sync up the physics with reality" method 
        # keeps the smooth scrolling effects aligned with the actual ScrollView state
        self._update_effect_x_bounds()
        self._update_effect_y_bounds()

    def _update_effect_x(self, *args):
        vp = self._viewport
        if not vp or not self.effect_x:
            return

        if self.effect_x.is_manual:
            sw = vp.width - self._effect_x_start_width
        else:
            sw = vp.width - self.width
        if sw < 1 and not (self.always_overscroll and self.do_scroll_x):
            return
        if sw != 0:
            sx = self.effect_x.scroll / sw
            self.scroll_x = -sx
        self._trigger_update_from_scroll()

    def _update_effect_y(self, *args):
        vp = self._viewport
        if not vp or not self.effect_y:
            return
        if self.effect_y.is_manual:
            sh = vp.height - self._effect_y_start_height
        else:
            sh = vp.height - self.height

        if sh < 1 and not (self.always_overscroll and self.do_scroll_y):
            return
        if sh != 0:
            sy = self.effect_y.scroll / sh
            self.scroll_y = -sy
        self._trigger_update_from_scroll()

    def to_local(self, x, y, **k):
        tx, ty = self.g_translate.xy
        return x - tx, y - ty

    def to_parent(self, x, y, **k):
        tx, ty = self.g_translate.xy
        return x + tx, y + ty

    def _apply_transform(self, m, pos=None):
        tx, ty = self.g_translate.xy
        m.translate(tx, ty, 0)
        return super(ScrollView, self)._apply_transform(m, (0, 0))

    def simulate_touch_down(self, touch):
        # CONTROLLED TOUCH RE-DISPATCH TO CHILD WIDGETS
        # ==============================================
        # This method safely re-dispatches touch events to child widgets, typically
        # used when a touch gesture is determined to be a click rather than a scroll.
        touch.push()
        touch.apply_transform_2d(self.to_local)
        
        # Store original grab state to restore later if needed
        original_grab_current = getattr(touch, 'grab_current', None)
        
        # Only ungrab nested manager if we're currently grabbed by it
        # This prevents interfering with the manager's touch_up handling
        if 'nsvm' in touch.ud and touch.grab_current == touch.ud['nsvm']['nested_managed']:
            touch.ungrab(touch.ud['nsvm']['nested_managed'])  
            
        ret = super(ScrollView, self).on_touch_down(touch)
        
        # If we ungrabbed the manager and no child grabbed the touch, restore the grab
        # This ensures the manager can still handle touch_up properly
        if ('nsvm' in touch.ud and 
            original_grab_current == touch.ud['nsvm']['nested_managed'] and 
            touch.grab_current is None):
            touch.grab(touch.ud['nsvm']['nested_managed'])
            
        touch.pop()
        return ret

    def on_motion(self, etype, me):
        if me.type_id in self.motion_filter and 'pos' in me.profile:
            me.push()
            me.apply_transform_2d(self.to_local)
            ret = super().on_motion(etype, me)
            me.pop()
            return ret
        return super().on_motion(etype, me)

    def _delegate_to_children(self, touch, method_name, check_collision=True):
        # Generic helper function to safely delegate touch events to child widgets.
        # Handles coordinate transformation and returns the result.
        # Args:
        #   touch: The touch event to delegate
        #   method_name: The method name to call (e.g., 'on_touch_move', 'on_touch_up')
        #   check_collision: Whether to check collision before delegating (default: True)
        # Returns: True if any child handled the touch, False otherwise
        if check_collision and not self.collide_point(*touch.pos):
            return False
            
        touch.push()
        touch.apply_transform_2d(self.to_local)
        res = getattr(super(ScrollView, self), method_name)(touch)
        touch.pop()
        return res

    def _delegate_touch_up_to_children_widget_coords(self, touch):
        # Delegate touch_up to children using widget coordinates (no collision check).
        touch.push()
        touch.apply_transform_2d(self.to_widget)
        res = super(ScrollView, self).on_touch_up(touch)
        touch.pop()
        return res

    def on_touch_down(self, touch):
        # STANDALONE SCROLLVIEW TOUCH HANDLING
        # ====================================
        # This method is only used when ScrollView operates standalone (not under
        # NestedScrollViewManager). For nested scenarios, NestedScrollViewManager
        # handles touch routing and calls on_scroll_start directly.
        if not self.collide_point(*touch.pos):
            return False
        if self.dispatch('on_scroll_start', touch):
            touch.grab(self)
            return True
        return False

    def _touch_in_handle(self, pos, size, touch):
        # check if the touch is in the handle of the scrollview
        # thouching the handle allows the user to drag the scrollview
        # clicking in the bar, and not the handle, jumps to that position in the scrollview
        x, y = pos
        width, height = size
        return x <= touch.x <= x + width and y <= touch.y <= y + height

    #
    # TOUCH USER DATA (touch.ud) KEY DOCUMENTATION
    # ============================================
    # This section documents all touch.ud keys used across ScrollView,
    # NestedScrollViewManager, and their interaction with Kivy's DragBehavior.
    # 
    # KEY NAMING CONVENTIONS:
    # ----------------------
    # 
    # SHARED 'sv.' NAMESPACE (Gesture Widget Coordination):
    # -----------------------------------------------------
    # Both ScrollView and DragBehavior use 'sv.' prefixed keys via their _get_uid()
    # methods to coordinate gesture ownership. This shared namespace allows widgets
    # to detect when a touch is being used for gestures (scrolling/dragging) vs
    # normal widget interactions (button clicks, etc).
    #
    # Per-ScrollView Instance Keys:
    # - sv.<uid>: Primary state dict for this ScrollView instance
    #   Contains: {
    #     'mode': str,          # 'unknown' (detecting intent) -> 'scroll' (confirmed)
    #     'dx': float,          # accumulated absolute X movement for detection
    #     'dy': float,          # accumulated absolute Y movement for detection  
    #     'scroll_action': bool,# True if scroll bars used or scroll performed
    #     'frames': int,        # Clock.frames at touch start (slow device timing)
    #     'can_defocus': bool,  # Whether this touch can defocus focused widgets
    #     'time': float,        # Touch timestamp for velocity calculations
    #     'dt': float,          # Delta time between updates
    #     'user_stopped': bool  # Whether user actively stopped scrolling
    #   }
    #
    # - svavoid.<uid>: Flag indicating this ScrollView should avoid handling this touch
    #   Set when: Mouse wheel events are handled, or touch doesn't collide
    #   Purpose: Prevents double-processing of already-handled touches
    #
    # Cross-ScrollView Shared Keys:
    # - sv.handled: dict {'x': bool, 'y': bool}
    #   Purpose: Tracks which axes have been processed by a ScrollView
    #   Used by: NestedScrollViewManager for orthogonal delegation
    #   Lifecycle: Set at start of on_touch_move, updated during scroll processing
    #
    # - sv.can_defocus: bool
    #   Purpose: Controls whether FocusBehavior should defocus on this touch
    #   Set to False when: Touch results in actual scrolling
    #   Used in: on_touch_up to prevent defocus after scroll gestures
    #
    # NESTEDSCROLLVIEWMANAGER NAMESPACE:
    # -----------------------------------
    # - nsvm: dict - Manager state for nested ScrollView coordination
    #   Contains: {
    #     'nested_managed': NestedScrollViewManager instance,
    #     'mode': str  # 'inner' or 'outer' - which ScrollView handles this touch
    #   }
    #   Purpose: Routes touches between outer and inner ScrollViews
    #   Lifecycle: Set in manager's on_touch_down, used throughout touch lifecycle
    #
    # GLOBAL SCROLLBAR FLAGS (No Namespacing Required):
    # --------------------------------------------------
    # - in_bar_x: bool - Touch started on horizontal scroll bar
    # - in_bar_y: bool - Touch started on vertical scroll bar
    #   Purpose: Differentiates bar dragging from content scrolling
    #   Affects: Touch routing, effect handling, movement calculations, delegation
    #   Rationale: Scroll bars are positioned at widget edges and cannot overlap,
    #              so multiple ScrollViews can safely share these global flags
    #
    # KIVY DRAGBEHAVIOR COORDINATION:
    # --------------------------------
    # DragBehavior (from kivy.uix.behaviors.drag) also uses 'sv.' prefixed keys
    # via its _get_uid() method. The check `if not any(key.startswith('sv.') ...)`
    # in on_touch_move allows ScrollView to detect when a touch is being used for
    # dragging and delegate to children appropriately. This prevents conflicts
    # between scrolling and dragging behaviors.
    #
    
    def _check_scroll_bounds(self, touch):
        """Check if touch is within scrollable bounds and set in_bar flags."""
        vp = self._viewport
        if not vp:
            return False, False
            
        # Calculate scrollable dimensions
        width_scrollable = (
            (self.always_overscroll and self.do_scroll_x)
            or vp.width > self.width
        )
        height_scrollable = (
            (self.always_overscroll and self.do_scroll_y)
            or vp.height > self.height
        )
        
        # Calculate distance from touch to scroll bar edges
        d = {
            'bottom': touch.y - self.y - self.bar_margin,
            'top': self.top - touch.y - self.bar_margin,
            'left': touch.x - self.x - self.bar_margin,
            'right': self.right - touch.x - self.bar_margin
        }
        
        # Check if touch is in horizontal or vertical scroll bars
        scroll_bar = 'bars' in self.scroll_type
        in_bar_x = (scroll_bar and width_scrollable and
                    (0 <= d[self.bar_pos_x] <= self.bar_width))
        in_bar_y = (scroll_bar and height_scrollable and
                    (0 <= d[self.bar_pos_y] <= self.bar_width))
                    
        return in_bar_x, in_bar_y

    def _handle_mouse_wheel_scroll(self, touch, btn, in_bar_x, in_bar_y):
        """Handle mouse wheel scrolling with nested routing logic."""
        m = self.scroll_wheel_distance
        
        # NESTED WHEEL ROUTING LOGIC:
        # Critical for nested ScrollViews - prevents inner SV from consuming
        # wheel events it can't handle, allowing outer SV to process them.
        # TODO: modify touch ud as required when returning False
        
        if btn in self._MOUSE_WHEEL_HORIZONTAL:
            # Horizontal wheel: only handle if we can scroll horizontally
            if not (self.do_scroll_x and (
                    (self.always_overscroll and self.do_scroll_x) or
                    (self._viewport and self._viewport.width > self.width)
            )):
                return False  # Pass to outer ScrollView
        elif btn in self._MOUSE_WHEEL_VERTICAL:
            # Vertical wheel: only handle if we can scroll vertically
            if not (self.do_scroll_y and (
                    (self.always_overscroll and self.do_scroll_y) or
                    (self._viewport and self._viewport.height > self.height)
            )):
                return False  # Pass to outer ScrollView
                
        # Check if we're at scroll boundaries
        if self._is_at_scroll_boundary(btn):
            return False
            
        # Select appropriate scroll effect
        e = self._select_scroll_effect_for_wheel(btn, in_bar_x, in_bar_y)
        if not e:
            return False
            
        # Apply wheel scroll movement
        self._apply_wheel_scroll(e, btn, m)
        e.trigger_velocity_update()
        return True

    def _is_at_scroll_boundary(self, btn):
        """Check if scroll is at boundary for the given wheel direction."""
        if (btn in self._MOUSE_WHEEL_VERTICAL and 
            ((btn == 'scrolldown' and self.scroll_y >= 1) or
             (btn == 'scrollup' and self.scroll_y <= 0))):
            return True
        if (btn in self._MOUSE_WHEEL_HORIZONTAL and
            ((btn == 'scrollleft' and self.scroll_x >= 1) or
             (btn == 'scrollright' and self.scroll_x <= 0))):
            return True
        return False

    def _select_scroll_effect_for_wheel(self, btn, in_bar_x, in_bar_y):
        """Select the appropriate scroll effect for mouse wheel scrolling."""
        vp = self._viewport
        if not vp:
            return None
            
        width_scrollable = (
            (self.always_overscroll and self.do_scroll_x)
            or vp.width > self.width
        )
        height_scrollable = (
            (self.always_overscroll and self.do_scroll_y)
            or vp.height > self.height
        )
        
        if (self.effect_x and self.do_scroll_y and height_scrollable and 
            btn in self._MOUSE_WHEEL_VERTICAL):
            return self.effect_x if in_bar_x else self.effect_y
        elif (self.effect_y and self.do_scroll_x and width_scrollable and 
              btn in self._MOUSE_WHEEL_HORIZONTAL):
            return self.effect_y if in_bar_y else self.effect_x
        return None

    def _apply_wheel_scroll(self, effect, btn, distance):
        """Apply wheel scroll movement to the selected effect."""
        # Sync effect bounds before applying scroll
        self._update_effect_bounds()
        
        if btn in self._MOUSE_WHEEL_DECREASE:
            if self.smooth_scroll_end:
                effect.velocity -= distance * self.smooth_scroll_end
            else:
                if self.always_overscroll:
                    effect.value = effect.value - distance
                else:
                    effect.value = max(effect.value - distance, effect.max)
                effect.velocity = 0
        elif btn in self._MOUSE_WHEEL_INCREASE:
            if self.smooth_scroll_end:
                effect.velocity += distance * self.smooth_scroll_end
            else:
                if self.always_overscroll:
                    effect.value = effect.value + distance
                else:
                    effect.value = min(effect.value + distance, effect.min)
                effect.velocity = 0


    def _handle_scrollbar_jump(self, touch, in_bar_x, in_bar_y):
        """Handle scrollbar position jump when clicking in bar but not handle."""
        ud = touch.ud
        if in_bar_y and not self._touch_in_handle(self._handle_y_pos, self._handle_y_size, touch):
            self.scroll_y = (touch.y - self.y) / self.height
        elif in_bar_x and not self._touch_in_handle(self._handle_x_pos, self._handle_x_size, touch):
            self.scroll_x = (touch.x - self.x) / self.width
        
        e = self.effect_y if in_bar_y else self.effect_x
        if e:
            self._update_effect_bounds()
            e.velocity = 0
            e.overscroll = 0
            e.trigger_velocity_update()

    def _initialize_scroll_effects(self, touch, in_bar):
        """Initialize scroll effects for both axes if enabled."""
        if self.do_scroll_x and self.effect_x and not in_bar:
            self._update_effect_bounds()
            self._effect_x_start_width = self.width
            self.effect_x.start(touch.x)
        
        if self.do_scroll_y and self.effect_y and not in_bar:
            self._update_effect_bounds()
            self._effect_y_start_height = self.height
            self.effect_y.start(touch.y)

    def _should_delegate_orthogonal(self, touch):
        """Check if touch movement is orthogonal to scroll direction.
        
        CRITICAL: Only delegate in truly ORTHOGONAL nested setups where:
        - Inner scrollview doesn't support the movement direction
        - Outer scrollview DOES support the movement direction
        
        For PARALLEL setups (both scroll same direction), orthogonal delegation
        should NEVER occur - touch stays with originally touched scrollview.
        """
        # If not in a nested managed setup, don't delegate
        if 'nsvm' not in touch.ud or touch.ud['nsvm'].get('mode') != 'inner':
            return False
        
        # Get the outer scrollview to check if it can handle orthogonal movement
        manager = touch.ud['nsvm'].get('nested_managed')
        if not manager or not manager.outer_scrollview:
            return False
        
        outer = manager.outer_scrollview
        
        abs_dx = abs(touch.dx)
        abs_dy = abs(touch.dy)
        
        # Only delegate if:
        # 1. Movement is SIGNIFICANTLY orthogonal (2x threshold to avoid noise)
        # 2. AND outer scrollview CAN scroll in that direction
        
        # Horizontal movement that inner can't handle, but outer can
        if abs_dx > abs_dy * 2 and not self.do_scroll_x and outer.do_scroll_x:
            return True
        
        # Vertical movement that inner can't handle, but outer can
        if abs_dy > abs_dx * 2 and not self.do_scroll_y and outer.do_scroll_y:
            return True
        
        return False

    def _should_lock_at_boundary(self, touch):
        """Check if scroll should lock at boundary (stop scrolling inner, no delegation in same gesture).
        
        Implements web-style boundary locking based on delegation_mode:
        - 'unknown': Never lock (touch did not start at boundary)
        - 'start_at_boundary': Check if moving away from boundary → transition to 'locked' OR moved into content → 'unknown'
        - 'locked': Already locked, keep inner from scrolling
        
        Returns True if inner scrollview should stop scrolling (locked state).
        Does NOT cause delegation to outer - that only happens on NEW touch.
        """
        # CRITICAL: Only check boundary locking if parallel_delegation is enabled
        # Otherwise, touches should never be locked/delegated based on boundaries
        if 'nsvm' not in touch.ud:
            return False
        
        manager = touch.ud['nsvm'].get('nested_managed')
        if not manager or not manager.parallel_delegation:
            return False
        
        delegation_mode = touch.ud.get('nsvm', {}).get('delegation_mode', 'unknown')
        
        # If not in delegation mode, never lock
        if delegation_mode == 'unknown':
            return False
        
        # If already locked, keep it locked (inner doesn't scroll, stays locked for this gesture)
        if delegation_mode == 'locked':
            print(f"Inner ScrollView: delegation_mode='locked', inner scrollview locked (not scrolling, not delegating)")
            return True
        
        # delegation_mode == 'start_at_boundary'
        # Check if we're trying to scroll beyond the boundary OR moved away into content
        abs_dx = abs(touch.dx)
        abs_dy = abs(touch.dy)
        
        if self.do_scroll_x and abs_dx > abs_dy:  # Horizontal scrolling
            # Check if we've moved away from the boundary into content
            if 0.05 < self.scroll_x < 0.95:
                print(f"Inner ScrollView: Moved away from boundary into content → canceling lock (scroll_x={self.scroll_x:.3f})")
                touch.ud['nsvm']['delegation_mode'] = 'unknown'
                return False
            
            # At right boundary trying to scroll left (beyond)
            if touch.dx < 0 and self.scroll_x >= 0.95:
                print(f"Inner ScrollView: At right boundary, scrolling beyond → locking inner (scroll_x={self.scroll_x:.3f}, dx={touch.dx:.1f})")
                touch.ud['nsvm']['delegation_mode'] = 'locked'
                return True
            # At left boundary trying to scroll right (beyond)
            elif touch.dx > 0 and self.scroll_x <= 0.05:
                print(f"Inner ScrollView: At left boundary, scrolling beyond → locking inner (scroll_x={self.scroll_x:.3f}, dx={touch.dx:.1f})")
                touch.ud['nsvm']['delegation_mode'] = 'locked'
                return True
                
        elif self.do_scroll_y and abs_dy > abs_dx:  # Vertical scrolling
            # Check if we've moved away from the boundary into content
            if 0.05 < self.scroll_y < 0.95:
                print(f"Inner ScrollView: Moved away from boundary into content → canceling lock (scroll_y={self.scroll_y:.3f})")
                touch.ud['nsvm']['delegation_mode'] = 'unknown'
                return False
            
            # At bottom boundary trying to scroll up (beyond)
            if touch.dy < 0 and self.scroll_y >= 0.95:
                print(f"Inner ScrollView: At bottom boundary, scrolling beyond → locking inner (scroll_y={self.scroll_y:.3f}, dy={touch.dy:.1f})")
                touch.ud['nsvm']['delegation_mode'] = 'locked'
                return True
            # At top boundary trying to scroll down (beyond)
            elif touch.dy > 0 and self.scroll_y <= 0.05:
                print(f"Inner ScrollView: At top boundary, scrolling beyond → locking inner (scroll_y={self.scroll_y:.3f}, dy={touch.dy:.1f})")
                touch.ud['nsvm']['delegation_mode'] = 'locked'
                return True
        
        return False

    def _process_scroll_axis_x(self, touch, not_in_bar):
        """Process X-axis scroll movement."""
        if touch.ud['sv.handled']['x'] or not self.do_scroll_x or not self.effect_x:
            return False
        
        print(f"PROCESSING X-AXIS: do_scroll_x={self.do_scroll_x}, effect_x={self.effect_x}, handled={touch.ud['sv.handled']['x']}")
        width = self.width
        if touch.ud.get('in_bar_x', False):
            if self.hbar[1] != 1:
                dx = touch.dx / float(width - width * self.hbar[1])
                self.scroll_x = min(max(self.scroll_x + dx, 0.), 1.)
                self._trigger_update_from_scroll()
        elif not_in_bar:
            print(f"EFFECT UPDATE X: touch.x={touch.x}, self.effect_x={self.effect_x}")
            self.effect_x.update(touch.x)
        
        touch.ud['sv.handled']['x'] = True
        
        # Let effects handle boundary behavior (bouncing, overscroll)
        if self.scroll_x < 0 or self.scroll_x > 1:
            print(f"SCROLL BOUNDARY: scroll_x={self.scroll_x}, letting effects handle boundary behavior")
        
        touch.ud['sv.can_defocus'] = False
        return True

    def _process_scroll_axis_y(self, touch, not_in_bar):
        """Process Y-axis scroll movement."""
        if touch.ud['sv.handled']['y'] or not self.do_scroll_y or not self.effect_y:
            return False
        
        print(f"PROCESSING Y-AXIS: do_scroll_y={self.do_scroll_y}, effect_y={self.effect_y}, handled={touch.ud['sv.handled']['y']}")
        height = self.height
        if touch.ud.get('in_bar_y', False) and self.vbar[1] != 1.0:
            dy = touch.dy / float(height - height * self.vbar[1])
            self.scroll_y = min(max(self.scroll_y + dy, 0.), 1.)
            self._trigger_update_from_scroll()
        elif not_in_bar:
            print(f"EFFECT UPDATE Y: touch.y={touch.y}, effect_value_before={self.effect_y.value}")
            self.effect_y.update(touch.y)
            print(f"EFFECT UPDATE Y: effect_value_after={self.effect_y.value}, scroll_y={self.scroll_y}")
            self._trigger_update_from_scroll()
        
        touch.ud['sv.handled']['y'] = True
        
        # Let effects handle boundary behavior (bouncing, overscroll)
        if self.scroll_y < 0 or self.scroll_y > 1:
            print(f"SCROLL BOUNDARY: scroll_y={self.scroll_y}, letting effects handle boundary behavior")
        
        touch.ud['sv.can_defocus'] = False
        return True

    def _stop_scroll_effects(self, touch, not_in_bar):
        """Stop scroll effects for both axes with edge case handling.
        
        Edge case: If orthogonal/boundary delegation occurred on the first touch move,
        the effect was started but never updated, leaving insufficient history for stop().
        The try/except gracefully handles this edge case.
        """
        if self.do_scroll_x and self.effect_x and not_in_bar:
            try:
                self.effect_x.stop(touch.x)
            except IndexError:
                pass  # Effect was started but delegated before being used
        
        if self.do_scroll_y and self.effect_y and not_in_bar:
            try:
                self.effect_y.stop(touch.y)
            except IndexError:
                pass  # Effect was started but delegated before being used

    def on_scroll_start(self, touch, check_children=True):
        print(f"on_scroll_start: called for ScrollView, mode={touch.ud.get('nsvm', {}).get('mode', 'no_nsvm')}, scroll_y={self.scroll_y:.3f}")
        if not self.collide_point(*touch.pos):
            touch.ud[self._get_uid('svavoid')] = True
            return False

        if self.disabled:
            return True
        
        if self._touch or (not (self.do_scroll_x or self.do_scroll_y)):
            # When already handling a touch or scrolling is disabled for both
            # axes, re-dispatch the event to our child content so non-scroll
            # interactions (e.g., buttons) still work.
            return self.simulate_touch_down(touch)

        # handle mouse scrolling, only if the viewport size is bigger than the
        # scrollview size, and if the user allowed to do it
        vp = self._viewport
        if not vp:
            return True
        scroll_type = self.scroll_type
        ud = touch.ud
        # scroll_bar = 'bars' in scroll_type

        # Check if touch is in scroll bars and set in_bar flags
        in_bar_x, in_bar_y = self._check_scroll_bounds(touch)
        in_bar = in_bar_x or in_bar_y
        ud['in_bar_x'] = in_bar_x
        ud['in_bar_y'] = in_bar_y

        if 'button' in touch.profile and touch.button.startswith('scroll'):
            if self._handle_mouse_wheel_scroll(touch, touch.button, in_bar_x, in_bar_y):
                touch.ud[self._get_uid('svavoid')] = True
                return True
            return False
        
        if scroll_type == ['bars'] and not in_bar:
            return self.simulate_touch_down(touch)
        
        if in_bar:
            self._handle_scrollbar_jump(touch, in_bar_x, in_bar_y)

        # no mouse scrolling, the user is going to drag the scrollview with
        # this touch.
        self._touch = touch
        # set the touch state for this touch
        uid = self._get_uid()
        ud[uid] = {
            'mode': 'unknown',
            'dx': 0,
            'dy': 0,
            'scroll_action': in_bar,
            'frames': Clock.frames,
            'can_defocus': True,  # Default: allow defocus unless scrolling
            'time': touch.time_start,
        }

        # Initialize scroll effects for content scrolling
        self._initialize_scroll_effects(touch, in_bar)

        # WEB-STYLE BOUNDARY DELEGATION:
        # Check if this touch is starting at a scroll boundary
        # Only check ONCE per gesture - for the first scrollview touched
        # Subsequent scrollviews (e.g., outer receiving delegation) should skip this check
        if 'nsvm' in touch.ud and not in_bar:
            # Only check if delegation_mode hasn't been set yet for this gesture
            manager = touch.ud['nsvm'].get('nested_managed')
            if manager and manager.parallel_delegation:
                # Check if at boundary (tolerance 0.05)
                at_boundary_x = (self.do_scroll_x and 
                                (self.scroll_x <= 0.05 or self.scroll_x >= 0.95))
                at_boundary_y = (self.do_scroll_y and 
                                (self.scroll_y <= 0.05 or self.scroll_y >= 0.95))
                    
                # Set delegation_mode based on boundary state
                if at_boundary_x or at_boundary_y:
                    touch.ud['nsvm']['delegation_mode'] = 'start_at_boundary'
                    print(f"ScrollView: Touch started at boundary, delegation_mode='start_at_boundary' (scroll_x={self.scroll_x:.3f}, scroll_y={self.scroll_y:.3f})")
                else:
                    # Leave as 'unknown' - no delegation will occur
                    print(f"ScrollView: Touch started NOT at boundary, delegation_mode='unknown' (scroll_x={self.scroll_x:.3f}, scroll_y={self.scroll_y:.3f})")

        if not in_bar:
            Clock.schedule_once(self._change_touch_mode,
                                self.scroll_timeout / 1000.)
        return True

    def on_touch_move(self, touch):
        print(f"on_touch_move: entered in update_sv.py")
        
        # SINGLE-TOUCH POLICY: Only process our designated touch
        if self._touch is not touch:
            print(f"on_touch_move: self._touch is not touch, delegating to children")
            return self._delegate_to_children(touch, 'on_touch_move')
        
        # Ensure we have grab ownership before processing
        if touch.grab_current is not self:
            print(f"on_touch_move: touch.grab_current is not self")
            return True
        
        
        # GESTURE WIDGET COORDINATION CHECK
        # =================================
        # Check if any gesture-handling widget (ScrollView or DragBehavior) has 
        # established state for this touch by looking for 'sv.' prefixed keys.
        # Both ScrollView and DragBehavior use the shared 'sv.' namespace via 
        # their _get_uid() methods to coordinate touch ownership.
        #
        # If NO 'sv.' keys exist, neither scrolling nor dragging is active,
        # so this touch should be passed to child widgets (buttons, etc.)
        # to prevent crashes and ensure proper widget interaction.
        if not any(isinstance(key, str) and key.startswith('sv.')
                   for key in touch.ud):
            # Handle dragged widgets - pass to children to prevent crashes
            print(f"on_touch_move: any(isinstance(key, str) and key.startswith('sv.'))")
            return self._delegate_to_children(touch, 'on_touch_move')
        
        # DIRECT SCROLL DISPATCH: 
        # touch.grab_current is current scrollview; primary touch, 
        # Initialize axis handling state and dispatch to scroll logic
        touch.ud['sv.handled'] = {'x': False, 'y': False}
        print(f"on_touch_move: dispatching to on_scroll_move")
        return self.dispatch('on_scroll_move', touch)


    def on_scroll_move(self, touch):
        print(f"on_scroll_move: touch.ud: {touch.ud}")
        if self._get_uid('svavoid') in touch.ud: 
            print(f"on_scroll_move: svavoid in touch.ud")
            return False

        rv = True
        # By default this touch can be used to defocus currently focused
        # widget, like any touch outside of ScrollView.
        touch.ud['sv.can_defocus'] = True
        
        uid = self._get_uid()  
        # if not 'nsvm' in touch.ud:
        if uid not in touch.ud:
            print(f"on_scroll_move: uid not in touch.ud")
            self._touch = False
            return self.on_scroll_start(touch, False)
        ud = touch.ud[uid]

        # check if the minimum distance has been travelled
        if ud['mode'] == 'unknown':
            if not (self.do_scroll_x or self.do_scroll_y):
                # touch is in parent, but _change expects window coords
                touch.push()
                touch.apply_transform_2d(self.to_local)
                touch.apply_transform_2d(self.to_window)
                self._change_touch_mode()
                touch.pop()
                return False
            ud['dx'] += abs(touch.dx)
            ud['dy'] += abs(touch.dy)
            print(f"on_scroll_move: ud['dx'] += abs(touch.dx): {ud['dx']}")
            print(f"on_scroll_move: ud['dy'] += abs(touch.dy): {ud['dy']}")
            

            # Transition to scroll mode if movement exceeds threshold on any axis
            # This allows orthogonal delegation to work properly
            if (ud['dx'] > self.scroll_distance or ud['dy'] > self.scroll_distance):
                ud['mode'] = 'scroll'

        if ud['mode'] == 'scroll':
            print(f"SCROLL MODE ACTIVE: ScrollView {self} processing touch in scroll mode")
            # NESTED SCROLLVIEW DELEGATION CHECK:
            # Only inner ScrollViews should delegate to outer ScrollViews
            # Outer ScrollViews (mode='outer') should not delegate further
            # Check if scrolling via scrollbar or content
            not_in_bar = not touch.ud.get('in_bar_x', False) and \
                not touch.ud.get('in_bar_y', False)
            
            # NESTED SCROLLVIEW DELEGATION (only for content scrolling, NOT scrollbar dragging)
            if 'nsvm' in touch.ud and touch.ud['nsvm'].get('mode') == 'inner' and not_in_bar:
                # ORTHOGONAL DELEGATION: delegate if movement is in unsupported direction
                if self._should_delegate_orthogonal(touch):
                    print(f"Inner ScrollView: Orthogonal movement detected - delegating (dx:{touch.dx:.1f}, dy:{touch.dy:.1f})")
                    print(f"ScrollView capabilities: do_scroll_x={self.do_scroll_x}, do_scroll_y={self.do_scroll_y}")
                    return False  # Let manager handle delegation
                
                # PARALLEL BOUNDARY DELEGATION: delegate if at scroll boundary in parallel setup
                # Only delegate when trying to scroll BEYOND the boundary (can't scroll further)
                # Only applies to CONTENT scrolling, not scrollbar dragging
                if self._should_lock_at_boundary(touch):
                    print(f"Inner ScrollView: Boundary delegation - passing to outer ScrollView")
                    return False  # Let manager handle delegation to outer

            # Process scroll movement for each axis
            self._process_scroll_axis_x(touch, not_in_bar)
            self._process_scroll_axis_y(touch, not_in_bar)
            ud['dt'] = touch.time_update - ud['time']
            ud['time'] = touch.time_update
            ud['user_stopped'] = True
        print(f"on_scroll_move: rv: {rv}")
        return rv



    def on_touch_up(self, touch):
        # TOUCH RELEASE HANDLING AND CLEANUP
        # ===================================
        # This method handles touch release events and ensures proper cleanup
        # of scroll state, grab ownership, and focus behavior. Critical for
        # preventing lingering touch ownership in nested ScrollView scenarios.
        
        # CASE 1: This ScrollView has state for this touch (previously handled it)
        # Even if self._touch is None now, we need to clean up properly
        print(f"on_touch_up: in update_sv.py")
        uid_key = self._get_uid()
        if uid_key in touch.ud:
            # Deliver scroll stop event and clean up grab ownership
            # This is critical to prevent lingering grab ownership that can
            # interfere with subsequent touches in nested ScrollViews
            self.dispatch('on_scroll_stop', touch)
            
            # Double-check grab ownership after on_scroll_stop handlers run
            # Some handlers might have already released the grab
            gl = touch.grab_list or []
            if any(w() is self for w in gl):
                touch.ungrab(self)
                
            # Handle focus behavior - if touch caused scrolling, prevent defocus
            if not touch.ud[uid_key].get('can_defocus', True):
                FocusBehavior.ignored_touch.append(touch)
            return True

        # CASE 2: This ScrollView is not handling this touch
        # id a button in the ScrollView is pressed, 
        # we need to pass the touch up event to children
        uid = self._get_uid('svavoid')
        if self._touch is not touch and uid not in touch.ud:
            return self._delegate_to_children(touch, 'on_touch_up')

        # CASE 3: Normal scroll stop handling
        # This ScrollView is actively handling this touch
        if self.dispatch('on_scroll_stop', touch):
            touch.ungrab(self)
            if not touch.ud[uid_key].get('can_defocus', True):
                # Touch caused scrolling - prevent focused widget defocus
                FocusBehavior.ignored_touch.append(touch)
            return True

    def on_scroll_stop(self, touch, check_children=True):
        # SCROLL COMPLETION AND FINAL CLEANUP
        # ====================================
        # This method handles the end of scroll gestures and performs final cleanup.
        # It handles multiple scenarios:
        # 1. Child widget scroll stop (nested ScrollViews)
        # 2. Effect stopping and cleanup
        # 3. Click passthrough for unrecognized gestures
        # 4. Mouse wheel event acknowledgment
        
        self._touch = None  # Clear our active touch reference

        # NOTE: NestedScrollViewManager will handle:
        # - Touch event routing between nested ScrollViews
        # - Preventing conflicts between inner/outer ScrollViews
        if self._get_uid('svavoid') in touch.ud or self._get_uid() not in touch.ud:
            return False

        uid = self._get_uid()
        ud = touch.ud[uid]
        
        # Determine if this was a scroll bar interaction
        not_in_bar = not touch.ud.get('in_bar_x', False) and \
            not touch.ud.get('in_bar_y', False)
            
        # Stop scroll effects if they were active (not for bar interactions)
        self._stop_scroll_effects(touch, not_in_bar)
            
        # CLICK PASSTHROUGH LOGIC
        # If the gesture never transitioned from 'unknown' to 'scroll' mode,
        # it means the user made a tap/click rather than a scroll gesture.
        # We need to simulate the click for child widgets to handle.
        if ud['mode'] == 'unknown':
            # Only simulate click if no scroll action occurred
            # (e.g., no scroll bar interaction or dragging)
            if not ud['scroll_action']:
                self.simulate_touch_down(touch)  # Let children handle the "click"
            # Schedule delayed touch up to complete the click simulation
            Clock.schedule_once(partial(self._do_touch_up, touch), .2)

        # Update effect bounds after scroll completion
        ev = self._update_effect_bounds_ev
        if ev is None:
            ev = self._update_effect_bounds_ev = Clock.create_trigger(
                self._update_effect_bounds)
        ev()

        # Always accept mouse wheel events
        if 'button' in touch.profile and touch.button.startswith('scroll'):
            return True

        # Return whether we had any involvement with this touch
        return self._get_uid() in touch.ud

    def scroll_to(self, widget, padding=10, animate=True):
        '''Scrolls the viewport to ensure that the given widget is visible,
        optionally with padding and animation. If animate is True (the
        default), then the default animation parameters will be used.
        Otherwise, it should be a dict containing arguments to pass to
        :class:`~kivy.animation.Animation` constructor.

        .. versionadded:: 1.9.1
        '''
        if not self.parent:
            return

        # if _viewport is layout and has pending operation, reschedule
        if hasattr(self._viewport, 'do_layout'):
            if self._viewport._trigger_layout.is_triggered:
                Clock.schedule_once(
                     lambda *dt: self.scroll_to(widget, padding, animate))
                return

        if isinstance(padding, (int, float)):
            padding = (padding, padding)

        pos = self.parent.to_widget(*widget.to_window(*widget.pos))
        cor = self.parent.to_widget(*widget.to_window(widget.right,
                                                      widget.top))

        dx = dy = 0

        if pos[1] < self.y:
            dy = self.y - pos[1] + dp(padding[1])
        elif cor[1] > self.top:
            dy = self.top - cor[1] - dp(padding[1])

        if pos[0] < self.x:
            dx = self.x - pos[0] + dp(padding[0])
        elif cor[0] > self.right:
            dx = self.right - cor[0] - dp(padding[0])

        dsx, dsy = self.convert_distance_to_scroll(dx, dy)
        sxp = min(1, max(0, self.scroll_x - dsx))
        syp = min(1, max(0, self.scroll_y - dsy))

        # Stop any existing motion before starting new animation
        if self.effect_x:
            self.effect_x.halt()
        if self.effect_y:
            self.effect_y.halt()

        if animate:
            if animate is True:
                animate = {'d': 0.2, 't': 'out_quad'}
            Animation.stop_all(self, 'scroll_x', 'scroll_y')
            Animation(scroll_x=sxp, scroll_y=syp, **animate).start(self)
        else:
            self.scroll_x = sxp
            self.scroll_y = syp

    def convert_distance_to_scroll(self, dx, dy):
        '''Convert a distance in pixels to a scroll distance, depending on the
        content size and the scrollview size.

        The result will be a tuple of scroll distance that can be added to
        :data:`scroll_x` and :data:`scroll_y`
        '''
        if not self._viewport:
            return 0, 0
        vp = self._viewport
        if vp.width > self.width:
            sw = vp.width - self.width
            sx = dx / float(sw)
        else:
            sx = 0
        if vp.height > self.height:
            sh = vp.height - self.height
            sy = dy / float(sh)
        else:
            sy = 1
        return sx, sy

    def update_from_scroll(self, *largs):
        '''Force the reposition of the content, according to current value of
        :attr:`scroll_x` and :attr:`scroll_y`.

        This method is automatically called when one of the :attr:`scroll_x`,
        :attr:`scroll_y`, :attr:`pos` or :attr:`size` properties change, or
        if the size of the content changes.
        '''
        if not self._viewport:
            self.g_translate.xy = self.pos
            return
        vp = self._viewport

        # update from size_hint
        if vp.size_hint_x is not None:
            w = vp.size_hint_x * self.width
            if vp.size_hint_min_x is not None:
                w = max(w, vp.size_hint_min_x)
            if vp.size_hint_max_x is not None:
                w = min(w, vp.size_hint_max_x)
            vp.width = w

        if vp.size_hint_y is not None:
            h = vp.size_hint_y * self.height
            if vp.size_hint_min_y is not None:
                h = max(h, vp.size_hint_min_y)
            if vp.size_hint_max_y is not None:
                h = min(h, vp.size_hint_max_y)
            vp.height = h

        if vp.width > self.width or self.always_overscroll:
            sw = vp.width - self.width
            x = self.x - self.scroll_x * sw
        else:
            x = self.x

        if vp.height > self.height or self.always_overscroll:
            sh = vp.height - self.height
            y = self.y - self.scroll_y * sh
        else:
            y = self.top - vp.height

        # from 1.8.0, we now use a matrix by default, instead of moving the
        # widget position behind. We set it here, but it will be a no-op most
        # of the time.
        vp.pos = 0, 0
        self.g_translate.xy = x, y

        # New in 1.2.0, show bar when scrolling happens and (changed in 1.9.0)
        # fade to bar_inactive_color when no scroll is happening.
        ev = self._bind_inactive_bar_color_ev
        if ev is None:
            ev = self._bind_inactive_bar_color_ev = Clock.create_trigger(
                self._bind_inactive_bar_color, .5)
        self.funbind('bar_inactive_color', self._change_bar_color)
        Animation.stop_all(self, '_bar_color')
        self.fbind('bar_color', self._change_bar_color)
        self._bar_color = self.bar_color
        ev()

    def _bind_inactive_bar_color(self, *args):
        self.funbind('bar_color', self._change_bar_color)
        self.fbind('bar_inactive_color', self._change_bar_color)
        Animation(
            _bar_color=self.bar_inactive_color,
            d=.5, t='out_quart').start(self)

    def _change_bar_color(self, inst, value):
        self._bar_color = value

    def add_widget(self, widget, *args, **kwargs):
        if self._viewport:
            raise Exception('ScrollView accept only one widget')
        canvas = self.canvas
        self.canvas = self.canvas_viewport
        super(ScrollView, self).add_widget(widget, *args, **kwargs)
        self.canvas = canvas
        self._viewport = widget
        widget.bind(size=self._trigger_update_from_scroll,
                    size_hint_min=self._trigger_update_from_scroll)
        self._trigger_update_from_scroll()

    def remove_widget(self, widget, *args, **kwargs):
        canvas = self.canvas
        self.canvas = self.canvas_viewport
        super(ScrollView, self).remove_widget(widget, *args, **kwargs)
        self.canvas = canvas
        if widget is self._viewport:
            self._viewport = None

    def _get_uid(self, prefix='sv'):
        # UNIQUE IDENTIFIER GENERATOR FOR TOUCH.UD KEYS
        # ==============================================
        # Generates unique keys for touch.ud (user data) dictionary based on
        # this ScrollView's unique ID. Critical for nested ScrollView coordination.
        #
        # USAGE PATTERNS:
        # - _get_uid() -> 'sv.123' (primary state key)
        # - _get_uid('svforce') -> 'svforce.123' (force re-dispatch flag)
        #
        # This ensures each ScrollView instance has its own namespace in
        # touch.ud, preventing conflicts in nested scenarios.
        return '{0}.{1}'.format(prefix, self.uid)

    def _change_touch_mode(self, *largs):
        # SCROLL TIMEOUT HANDLER - GESTURE DETECTION TIMEOUT
        # ==================================================
        # This method is called when the scroll_timeout expires without the touch
        # traveling the minimum scroll_distance. It transitions from scroll detection
        # mode to normal widget interaction mode by handing off the touch to child widgets.
        if not self._touch:
            return
            
        uid = self._get_uid()
        touch = self._touch
        if uid not in touch.ud:
            self._touch = False
            return
            
        ud = touch.ud[uid]
        # Only proceed if we're still in gesture detection mode
        if ud['mode'] != 'unknown' or ud['scroll_action']:
            return
            
        diff_frames = Clock.frames - ud['frames']

        # SLOW DEVICE PROTECTION:
        # On very slow devices, we need at least 3 frames to accumulate
        # velocity data. Otherwise, scroll effects might not work properly.
        # This addresses issues #1464 and #1499 for low-performance devices.
        if diff_frames < 3:
            Clock.schedule_once(self._change_touch_mode, 0)
            return

        # CLEANUP AND HANDOFF:
        # Cancel any scroll effects that may have started
        if self.do_scroll_x and self.effect_x:
            self.effect_x.cancel()
        if self.do_scroll_y and self.effect_y:
            self.effect_y.cancel()
            
        touch.ungrab(self)
        self._touch = None
        
        # CONTROLLED HANDOFF TO CHILD WIDGETS:
        # Transform touch coordinates and re-dispatch to children
        # This allows buttons, sliders, etc. to handle the touch normally
        # NOTE: Do NOT schedule _do_touch_up here - this is a live touch handoff,
        # not a synthetic click. The user is still holding their finger down.
        touch.push()
        touch.apply_transform_2d(self.to_widget)
        touch.apply_transform_2d(self.to_parent)
        
        self.simulate_touch_down(touch)
        touch.pop()
        return

    def _do_touch_up(self, touch, *largs):
        # Complete touch lifecycle by sending touch_up to all widgets that grabbed this touch.
        # Ensures proper cleanup for buttons/widgets that were touched during scroll gestures.
        # touch is in window coords
        self._delegate_touch_up_to_children_widget_coords(touch)
        # don't forget about grab event!
        for x in touch.grab_list[:]:
            touch.grab_list.remove(x)
            x = x()
            if not x:
                continue
            touch.grab_current = x
            # touch is in window coords
            self._delegate_touch_up_to_children_widget_coords(touch)
        touch.grab_current = None


if __name__ == '__main__':
    from kivy.app import App

    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.button import Button

    class ScrollViewApp(App):

        def build(self):
            layout1 = GridLayout(cols=4, spacing=10, size_hint=(None, None))
            layout1.bind(minimum_height=layout1.setter('height'),
                         minimum_width=layout1.setter('width'))
            for i in range(40):
                btn = Button(text=str(i), size_hint=(None, None),
                             size=(200, 100))
                layout1.add_widget(btn)
            scrollview1 = ScrollView(bar_width='2dp', smooth_scroll_end=10)
            scrollview1.add_widget(layout1)

            layout2 = GridLayout(cols=4, spacing=10, size_hint=(None, None))
            layout2.bind(minimum_height=layout2.setter('height'),
                         minimum_width=layout2.setter('width'))
            for i in range(40):
                btn = Button(text=str(i), size_hint=(None, None),
                             size=(200, 100))
                layout2.add_widget(btn)
            scrollview2 = ScrollView(scroll_type=['bars'],
                                     bar_width='9dp',
                                     scroll_wheel_distance=100)
            scrollview2.add_widget(layout2)

            root = GridLayout(cols=2)
            root.add_widget(scrollview1)
            root.add_widget(scrollview2)
            return root

    ScrollViewApp().run()
