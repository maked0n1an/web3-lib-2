class AutoRepr:
    """Contains a __repr__ function that automatically builds the output of a class using all its variables."""

    def __repr__(self) -> str:
        values = ('{}={!r}'.format(key, value)
                  for key, value in vars(self).items())
        return '{}({})'.format(self.__class__.__name__, ', '.join(values))


class Singleton(type):
    """A class that implements the singleton pattern."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(cls, *args, **kwargs)
        return cls._instances[cls]