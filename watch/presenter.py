import datetime

import yaml

from sismic.io import import_from_yaml
from sismic.model import Statechart
from sismic.interpreter import Interpreter

from .include import IncludeLoader
from .utils import get_resource_path


class Presenter:
    def __init__(self, view, model):
        with open(get_resource_path('statechart/watch.yml')) as f:
            statechart = yaml.load(f, Loader=IncludeLoader)
            statechart = import_from_yaml(text=yaml.dump(statechart))

        self.it = Interpreter(statechart)
        self.it.context["pr"] = self
        self.it.context["model"] = model
        self.it.clock.start()

        self._view = view
        self._view.schedule_once(self._run_interpreter, 0.1)
        self._view.set_event_callback(self.it.queue)

    def _run_interpreter(self):
        self._view.schedule_once(self._run_interpreter, 0.1)
        self.it.execute()

    def set_light(self, state):
        self._view.set_light(state)

    def _display_time(self, time, hour24):
        self._view.set_text("min", time.strftime("%M"))
        self._view.set_text("sec", time.strftime("%S"))

        if hour24:
            self._view.set_text("am_pm", time.strftime("%p"))
            self._view.set_text("hour", time.strftime("%I"))
        else:
            self._view.set_text("am_pm", "")
            self._view.set_text("hour", time.strftime("%H"))

    def _display_on_off(self, state):
        if state:
            self._view.set_text("sec", "ON")
        else:
            self._view.set_text("sec", "OFF")

    def update_disp_select(self, selected):
        for part in "hour", "min", "sec", "am_pm":
            if part == selected:
                self._view.set_text(part + "_sel", "-")
            else:
                self._view.set_text(part + "_sel", "")

    def update_display_time(self, time, hour24):
        self._display_time(time, hour24)

    def update_display_date(self, time):
        self._view.set_text("hour", time.strftime("%m"))
        self._view.set_text("min", time.strftime("%d"))
        self._view.set_text("sec", time.strftime("%y"))
        self._view.set_text("am_pm", time.strftime("%a"))

    def update_display_alarm(self, time, hour24, enabled):
        self._display_time(time, hour24)
        self._display_on_off(enabled)

    def update_display_chime(self, enabled):
        self._view.set_text("hour", "")
        self._view.set_text("min", "00")
        self._view.set_text("sec", "")
        self._view.set_text("am_pm", "")
        self._display_on_off(enabled)

    def update_display_stopwatch_zero(self):
        self._view.set_text("hour", "{:02}".format(0))
        self._view.set_text("min", "{:02}".format(0))
        self._view.set_text("sec", "{:02}".format(0))
        self._view.set_text("am_pm", "")

    def update_display_stopwatch(self, elapsed, stopped, time):
        if not stopped:
            elapsed += (datetime.datetime.today() - time)
        stopwatch_time = elapsed.total_seconds()

        total_mseconds = int(stopwatch_time * 1000)
        mseconds = total_mseconds % 1000
        total_seconds = total_mseconds // 1000
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60

        self._view.set_text("hour", "{:02}".format(minutes))
        self._view.set_text("min", "{:02}".format(seconds))
        self._view.set_text("sec", "{:02}".format(mseconds // 10))
        self._view.set_text("am_pm", "")

    def update_mode_selection(self, mode):
        for ind in self._view.icons.keys():
            if mode.startswith(ind):
                self._view.set_text(ind, self._view.icons[ind])
            else:
                self._view.set_text(ind, "")

    def update_indication_state(self, enabled):
        for ind in self._view.icons.keys():
            if enabled[ind]:
                self._view.set_text(ind, self._view.icons[ind])
            else:
                self._view.set_text(ind, "")

    def play(self, name, loop=False):
        self._view.play(name, loop)

    def stop(self):
        self._view.stop()

    def run(self):
        self._view.run()


