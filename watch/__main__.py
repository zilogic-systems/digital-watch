import sys

from .model import Model
from .presenter import Presenter

if len(sys.argv) != 2:
    print("watch: UI not specified")
    exit(1)

if sys.argv[1] == "gtk":
    from .view_gtk import GtkView as View

elif sys.argv[1] == "kivy":
    from .view_kivy import KivyView as View

else:
    print("watch: unsupported UI specified")
    exit(1)


model = Model()
presenter = Presenter()
view = View(presenter.it)

presenter.it.context["model"] = model
presenter.it.context["view"] = view

view.run()
