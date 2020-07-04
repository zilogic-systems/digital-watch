import yaml

from sismic.io import import_from_yaml
from sismic.model import Statechart
from sismic.interpreter import Interpreter

from .include import IncludeLoader
from .utils import get_resource_path


class Presenter():
    def __init__(self):
        with open(get_resource_path('statechart/watch.yml')) as f:
            statechart = yaml.load(f, Loader=IncludeLoader)
            statechart = import_from_yaml(text=yaml.dump(statechart))

        self.it = Interpreter(statechart)
        self.it.clock.start()

