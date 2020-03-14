import pelican

from .generators import get_generators


def register():
    pelican.signals.get_generators.connect(get_generators)
