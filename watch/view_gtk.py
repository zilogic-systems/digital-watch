import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('Gst', '1.0')
from gi.repository import Gst

from .utils import get_resource_path


class Player:
    def __init__(self, mainloop):
        Gst.init()
        self._player = Gst.ElementFactory.make("playbin", "player")
        bus = self._player.get_bus()
        bus.add_watch(0, self._play_loop, mainloop)
        self._in_loop = False

    def _play_loop(self, bus, msg, *args):
        if msg.type == Gst.MessageType.SEGMENT_DONE and self._in_loop:
            flags = Gst.SeekFlags.SEGMENT
            self._player.seek_simple(Gst.Format.TIME, flags, 0);

    def play(self, name, loop=False):
        self._player.set_property('uri','file://' + get_resource_path(name + '.mp3'))
        self._in_loop = loop
        self._player.set_state(Gst.State.PLAYING)

    def stop(self):
        self._player.set_state(Gst.State.NULL)


class GtkUI:
    icons = {
        "alarm1": "🔔",
        "alarm2": "🔔",
        "chime": "🎵",
        "stopwatch": "⏱",
    }

    def __init__(self):
        self._mainloop = GObject.MainLoop()
        self._player = Player(self._mainloop)
        self._builder = Gtk.Builder()
        self._builder.add_from_file(get_resource_path("watch.glade"))
        self._builder.connect_signals(self)
        self._interpreter = None

        self._setup_buttons()

        top_window = self._builder.get_object("top_window")
        top_window.show_all()

    def schedule_once(self, func, timeout):
        GObject.timeout_add(int(timeout * 1000), func)

    def set_event_callback(self, func):
        self._send_event = func

    def on_top_window_delete_event(self, *args):
        self._mainloop.quit()

    def _setup_buttons(self):
        for name in "a", "b", "c", "d":
            button = self._builder.get_object(name + "_button")

            def on_button_pressed(x, name=name):
                self._send_event(name + "_pressed")
                self._send_event("any_pressed")

            def on_button_released(x, name=name):
                self._send_event(name + "_released")
                self._send_event("any_released")

            button.connect("pressed", on_button_pressed)
            button.connect("released", on_button_released)

    def set_light(self, state):
        light_image = self._builder.get_object("light_image")

        if state:
            light_image.show()
        else:
            light_image.hide()

    def set_text(self, name, text):
        label = self._builder.get_object(name + "_label")
        label.set_text(text)

    def play(self, name, loop=False):
        self._player.play(name, loop)

    def stop(self):
        self._player.stop()

    def run(self):
        self._mainloop.run()
