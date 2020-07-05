import sys

from .model import Model
from .presenter import Presenter

if len(sys.argv) != 2:
    print("watch: UI not specified")
    exit(1)

if sys.argv[1] == "gtk":
    from .view_gtk import GtkUI as View

elif sys.argv[1] == "kivy":
    from .view_kivy import KivyUI as View

else:
    print("watch: unsupported UI specified")
    exit(1)


model = Model()
view = View()
pr = Presenter(view, model)

pr.run()
