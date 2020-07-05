from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader


class WatchApp(App):
    pass


class KivyUI:
    icons = {
        "alarm1": "\uF0F3",
        "alarm2": "\uF0F3",
        "chime": "\uF001",
        "stopwatch": "\uF2F2",
    }

    def __init__(self):
        self._interpreter = None
        self._app = WatchApp()

        self._sound = None
        self._widgets = None
        self._interpter = None
        Clock.schedule_once(self._setup_ui, 0)

    def schedule_once(self, func, timeout):
        Clock.schedule_once(lambda *args: func(), timeout)

    def set_event_callback(self, func):
        self._send_event = func

    def _setup_ui(self, *args):
        self._widgets = self._app.root.ids
        self._setup_buttons()

    def _setup_buttons(self, *args):
        for name in "a", "b", "c", "d":
            button = self._widgets[name + "_button"]

            def on_button_pressed(x, name=name):
                self._send_event(name + "_pressed")
                self._send_event("any_pressed")

            def on_button_released(x, name=name):
                self._send_event(name + "_released")
                self._send_event("any_released")

            button.bind(on_press=on_button_pressed)
            button.bind(on_release=on_button_released)

    def set_light(self, state):
        if state:
            self._widgets.light_label.opacity = 0.5
        else:
            self._widgets.light_label.opacity = 0

    def set_text(self, name, text):
        self._widgets[name + "_label"].text = text

    def play(self, name, loop=False):
        self._sound = SoundLoader.load(name + ".mp3")
        self._sound.play()

    def stop(self):
        if self._sound:
            self._sound.stop()

    def run(self):
        self._app.run()
