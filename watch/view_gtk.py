import time

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


class GtkView:
    icons = {
        "alarm1": "🔔",
        "alarm2": "🔔",
        "chime": "🎵",
        "stopwatch": "⏱",
    }

    def __init__(self, model, interpreter):
        self._model = model
        self._interpreter = interpreter

        self._mainloop = GObject.MainLoop()
        self._player = Player(self._mainloop)
        self._builder = Gtk.Builder()
        self._builder.add_from_file(get_resource_path("watch.glade"))
        self._builder.connect_signals(self)
        self._hour_label = self._builder.get_object("hour_label")
        self._min_label = self._builder.get_object("min_label")
        self._sec_label = self._builder.get_object("sec_label")
        self._am_pm_label = self._builder.get_object("am_pm_label")
        self._light_image = self._builder.get_object("light_image")

        self._setup_buttons()

        top_window = self._builder.get_object("top_window")
        top_window.show_all()

        GObject.timeout_add(100, self._run_sm)

    def set_light(self, state):
        if state:
            self._light_image.show()
        else:
            self._light_image.hide()

    def _display_time(self, time):
        self._min_label.set_text(time.strftime("%M"))
        self._sec_label.set_text(time.strftime("%S"))

        if not self._model.hour24:
            self._am_pm_label.set_text(time.strftime("%p"))
            self._hour_label.set_text(time.strftime("%I"))
        else:
            self._am_pm_label.set_text("")
            self._hour_label.set_text(time.strftime("%H"))

    def _display_on_off(self, state):
        if state:
            self._sec_label.set_text("ON")
        else:
            self._sec_label.set_text("OFF")

    def update_disp_select(self, selected):
        for part in "hour", "min", "sec", "am_pm":
            label = self._builder.get_object(part + "_sel_label")
            if part == selected:
                label.set_text("-")
            else:
                label.set_text("")

    def update_display_time(self):
        self._display_time(self._model.time["current"])

    def update_display_date(self):
        time = self._model.time["current"]
        self._hour_label.set_text(time.strftime("%m"))
        self._min_label.set_text(time.strftime("%d"))
        self._sec_label.set_text(time.strftime("%y"))
        self._am_pm_label.set_text(time.strftime("%a"))

    def update_display_alarm1(self):
        self._display_time(self._model.time["alarm1"])
        self._display_on_off(self._model.enabled["alarm1"])

    def update_display_alarm2(self):
        self._display_time(self._model.time["alarm2"])
        self._display_on_off(self._model.enabled["alarm2"])

    def update_display_chime(self):
        self._hour_label.set_text("")
        self._min_label.set_text("00")
        self._sec_label.set_text("")
        self._am_pm_label.set_text("")
        self._display_on_off(self._model.enabled["chime"])

    def update_display_stopwatch_zero(self):
        self._hour_label.set_text("{:02}".format(0))
        self._min_label.set_text("{:02}".format(0))
        self._sec_label.set_text("{:02}".format(0))
        self._am_pm_label.set_text("")

    def update_display_stopwatch(self):
        elapsed = model.stopw_elapsed
        if not self._model.stopw_stopped:
            elapsed += (datetime.datetime.today() - self._model.stopw_time)
        stopwatch_time = elapsed.total_seconds()

        total_mseconds = int(stopwatch_time * 1000)
        mseconds = total_mseconds % 1000
        total_seconds = total_mseconds // 1000
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60

        self._hour_label.set_text("{:02}".format(minutes))
        self._min_label.set_text("{:02}".format(seconds))
        self._sec_label.set_text("{:02}".format(mseconds // 10))
        self._am_pm_label.set_text("")

    def update_mode_selection(self, mode):
        for ind in self.icons.keys():
            label = self._builder.get_object(ind + "_label")
            if mode.startswith(ind):
                label.set_text(self.icons[ind])
            else:
                label.set_text("")

    def update_indication_state(self):
        for ind in self.icons.keys():
            label = self._builder.get_object(ind + "_label")
            if self._model.enabled[ind]:
                label.set_text(self.icons[ind])
            else:
                label.set_text("")

    def on_top_window_delete_event(self, *args):
        self._mainloop.quit()

    def _setup_buttons(self):
        for name in "a", "b", "c", "d":
            button = self._builder.get_object(name + "_button")

            def on_button_pressed(x, name=name):
                self._interpreter.queue(name + "_pressed")
                self._interpreter.queue("any_pressed")

            def on_button_released(x, name=name):
                self._interpreter.queue(name + "_released")
                self._interpreter.queue("any_released")

            button.connect("pressed", on_button_pressed)
            button.connect("released", on_button_released)

    def _run_sm(self):
        self._interpreter.execute()
        GObject.timeout_add(100, self._run_sm)

    def play(self, name, loop=False):
        self._player.play(name, loop)

    def stop(self):
        self._player.stop()

    def run(self):
        self._mainloop.run()
