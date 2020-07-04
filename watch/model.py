import datetime


def _time_after(after):
    t = datetime.datetime.today() + datetime.timedelta(seconds=after)
    return t.time().replace(microsecond=0)


class Model:
    def __init__(self):
        self.time = {}
        self.time["current"] = datetime.datetime.today()
        self.time["alarm1"] = _time_after(5)
        self.time["alarm2"] = _time_after(5)

        self.enabled = {
            "alarm1": True,
            "alarm2": True,
            "stopwatch": False,
            "chime": True,
        }

        self.stopw_time = datetime.datetime.today()
        self.stopw_elapsed = datetime.timedelta(seconds=0)
        self.stopw_stopped = True
        self.hour24 = False

    def zero_stopwatch(self):
        self.stopw_elapsed = datetime.timedelta(seconds=0)
        self.stopw_stopped = True

    def start_stopwatch(self):
        self.stopw_time = datetime.datetime.today()
        self.stopw_stopped = False

    def stop_stopwatch(self):
        self.stopw_elapsed += (datetime.datetime.today() - self.stopw_time)
        self.stopw_stopped = True

    def update_time(self):
        self.time["current"] += datetime.timedelta(seconds=1)

    def increment_sec(self, which):
        t = self.time[which]
        try:
            self.time[which] = t.replace(second=t.second+1)
        except ValueError:
            self.time[which] = t.replace(second=0)

    def increment_min(self, which):
        t = self.time[which]
        try:
            self.time[which] = t.replace(minute=t.minute+1)
        except ValueError:
            self.time[which] = t.replace(minute=0)

    def increment_hour(self, which):
        t = self.time[which]
        try:
            self.time[which] = t.replace(hour=(t.hour + 1) % 24)
        except ValueError:
            self.time[which] = t.replace(hour=0)

    def increment_day(self, which):
        t = self.time[which]
        try:
            self.time[which] = t.replace(day=t.day+1)
        except ValueError:
            self.time[which] = t.replace(day=1)

    def increment_month(self, which):
        t = self.time[which]
        try:
            self.time[which] = t.replace(month=t.month+1)
        except ValueError:
            self.time[which] = t.replace(month=1)

    def increment_year(self, which):
        t = self.time[which]
        new_year = t.year % 100
        new_year += 1
        new_year %= 100
        new_year += 2000
        self.time[which] = t.replace(year=new_year)

    def toggle_mode(self):
        self.hour24 = not self.hour24

    def is_hour(self):
        return (self.enabled["chime"] and
                self.time["current"].minute == 0 and
                self.time["current"].second == 0)

    def _has_fired_alarm(self, nalarm):
        now = self.time["current"].time().replace(microsecond=0)
        is_alarm = self.enabled[nalarm] and now == self.time[nalarm]
        return is_alarm

    def has_fired_alarm1(self):
        return self._has_fired_alarm("alarm1")

    def has_fired_alarm2(self):
        return self._has_fired_alarm("alarm2")


