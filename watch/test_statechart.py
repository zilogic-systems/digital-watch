from unittest.mock import Mock

import yaml

from sismic.io import import_from_yaml
from sismic.interpreter import Interpreter
from sismic.testing import state_is_entered

from .include import IncludeLoader
from .__main__ import get_resource_path
from .__main__ import Model


def load_interpreter():
    with open(get_resource_path('statechart/watch.yml')) as f:
        statechart = yaml.load(f, Loader=IncludeLoader)
        statechart = import_from_yaml(text=yaml.dump(statechart))

    return Interpreter(statechart)


def setup_statechart():
    view = Mock()
    model = Model()
    player = Mock()

    it = load_interpreter()
    it.context["view"] = view
    it.context["model"] = model
    it.context["player"] = player

    steps = it.execute()

    return it, view, model, player


def test_light_on():
    it, view, model, player = setup_statechart()
    
    it.queue("b_pressed").execute()

    view.set_light.assert_called_with(True)


def test_light_off():
    it, view, model, player = setup_statechart()

    it.queue("b_pressed").execute()
    it.queue("b_released").execute()

    view.set_light.assert_called_with(False)


def test_show_date():
    it, view, model, player = setup_statechart()

    it.queue("d_pressed").execute()
    it.queue("d_released").execute()

    assert view.update_display_date.called


def test_auto_hide_date():
    it, view, model, player = setup_statechart()

    it.queue("d_pressed").execute()
    it.queue("d_released").execute()

    it.clock.time += 10

    steps = it.execute()

    assert state_is_entered(steps, "time")


def test_manual_toggle_date():
    it, view, model, player = setup_statechart()
    it.queue("d_pressed").execute()
    it.queue("d_released").execute()
    
    steps = it.queue("d_pressed").execute()
    steps += it.queue("d_released").execute()

    assert state_is_entered(steps, "time")


def test_alarm1():
    it, view, model, player = setup_statechart()
    
    steps = it.queue("a_pressed").execute()
    steps += it.queue("a_released").execute()

    assert state_is_entered(steps, "alarm1")


    
