import os

__all__ = []
file = ''
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith('.py'):
        __all__.append(file[:-3])

del file
del os

from server import *
