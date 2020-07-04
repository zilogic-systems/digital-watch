# coding: utf-8

from .model import Model
from .presenter import Presenter
from .view_gtk import GtkView


if __name__ == "__main__":
    model = Model()
    presenter = Presenter()
    view = GtkView(model, presenter.it)

    presenter.it.context["model"] = model
    presenter.it.context["view"] = view

    presenter.it.execute_once()
    view.run()
