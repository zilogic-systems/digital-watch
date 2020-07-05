from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader


class WatchApp(App):
    pass


class KivyView:
    icons = {
        "alarm1": "\uF0F3",
        "alarm2": "\uF0F3",
        "chime": "\uF001",
        "stopwatch": "\uF2F2",
    }

    def __init__(self, model, interpreter):
        self._model = model
        self._interpreter = interpreter
        self._app = WatchApp()

        self._sound = None
        self._ui = None
        Clock.schedule_once(self._setup_ui, 0)

    def _setup_ui(self, *args):
        self._ui = self._app.root.ids
        self._setup_buttons()
        Clock.schedule_interval(self._run_sm, 0.1)

    def _setup_buttons(self, *args):
        for name in "a", "b", "c", "d":
            button = self._ui[name + "_button"]

            def on_button_pressed(x, name=name):
                self._interpreter.queue(name + "_pressed")
                self._interpreter.queue("any_pressed")

            def on_button_released(x, name=name):
                self._interpreter.queue(name + "_released")
                self._interpreter.queue("any_released")

            button.bind(on_press=on_button_pressed)
            button.bind(on_release=on_button_released)

    def _run_sm(self, *args):
        self._interpreter.execute()

    def _display_on_off(self, state):
        if state:
            self._ui.sec_label.text = "ON"
        else:
            self._ui.sec_label.text = "OFF"

    def set_light(self, state):
        if state:
            self._ui.light_label.opacity = 0.5
        else:
            self._ui.light_label.opacity = 0

    def update_disp_select(self, selected):
        for part in "hour", "min", "sec", "am_pm":
            label = self._ui[part + "_sel_label"]
            if part == selected:
                label.text = "-"
            else:
                label.text = ""

    def _display_time(self, time):
        self._ui.min_label.text = time.strftime("%M")
        self._ui.sec_label.text = time.strftime("%S")

        if not self._model.hour24:
            self._ui.am_pm_label.text = time.strftime("%p")
            self._ui.hour_label.text = time.strftime("%I")
        else:
            self._ui.am_pm_label.text = ""
            self._ui.hour_label.text = time.strftime("%H")

    def update_display_time(self):
        self._display_time(self._model.time["current"])

    def update_display_date(self):
        time = self._model.time["current"]
        self._ui.hour_label.text = time.strftime("%m")
        self._ui.min_label.text = time.strftime("%d")
        self._ui.sec_label.text = time.strftime("%y")
        self._ui.am_pm_label.text = time.strftime("%a")

    def update_display_alarm1(self):
        self._display_time(self._model.time["alarm1"])
        self._display_on_off(self._model.enabled["alarm1"])

    def update_display_alarm2(self):
        self._display_time(self._model.time["alarm2"])
        self._display_on_off(self._model.enabled["alarm2"])

    def update_display_chime(self):
        self._ui.hour_label.text = ""
        self._ui.min_label.text = "00"
        self._ui.sec_label.text = ""
        self._ui.am_pm_label.text = ""
        self._display_on_off(self._model.enabled["chime"])

    def update_display_stopwatch_zero(self):
        self._ui.hour_label.text = "{:02}".format(0)
        self._ui.min_label.text = "{:02}".format(0)
        self._ui.sec_label.text = "{:02}".format(0)
        self._ui.am_pm_label.text = ""

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

        self._ui.hour_label.text = "{:02}".format(minutes)
        self._ui.min_label.text = "{:02}".format(seconds)
        self._ui.sec_label.text = "{:02}".format(mseconds // 10)
        self._ui.am_pm_label.text = ""

    def update_mode_selection(self, mode):
        for ind in self.icons.keys():
            label = self._ui[ind + "_label"]
            if mode.startswith(ind):
                label.text = self.icons[ind]
            else:
                label.text = ""

    def update_indication_state(self):
        for ind in self.icons.keys():
            label = self._ui[ind + "_label"]
            if self._model.enabled[ind]:
                label.text = self.icons[ind]
            else:
                label.text = ""

    def play(self, name, loop=False):
        self._sound = SoundLoader.load(name + ".mp3")
        self._sound.play()

    def stop(self):
        if self._sound:
            self._sound.stop()

    def run(self):
        self._app.run()
