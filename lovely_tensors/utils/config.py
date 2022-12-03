# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/03_utils.config.ipynb.

# %% auto 0
__all__ = ['set_config', 'get_config', 'config']

# %% ../../nbs/03_utils.config.ipynb 3
from copy import copy
from types import SimpleNamespace
from typing import Optional, Union, Callable, TypeVar
from contextlib import contextmanager
from lovely_numpy import config as np_config

# %% ../../nbs/03_utils.config.ipynb 4
_defaults = SimpleNamespace(
    precision     = 3,    # Digits after `.`
    threshold_max = 3,    # .abs() larger than 1e3 -> Sci mode
    threshold_min = -4,   # .abs() smaller that 1e-4 -> Sci mode
    sci_mode      = None, # Sci mode (2.3e4). 
    indent        = 2,    # Indent for .deeper()
    color         = True, # ANSI colors in text
    deeper_width  = 9,    # For .deeper, how many entries to show per level
)

_config = copy(_defaults)

# %% ../../nbs/03_utils.config.ipynb 5
# Allows passing None as an argument to reset to defaults
class _Default():
    def __repr__(self):
        return "Ignore"
Default = _Default()
D = TypeVar("Default")

# %% ../../nbs/03_utils.config.ipynb 6
def set_config( precision       :Optional[Union[D, int]] =Default,  # Digits after `.`
                threshold_min   :Optional[Union[D,int]]  =Default,  # .abs() larger than 1e3 -> Sci mode
                threshold_max   :Optional[Union[D,int]]  =Default,  # .abs() smaller that 1e-4 -> Sci mode
                sci_mode        :Optional[Union[D,bool]] =Default,  # Sci mode (1.2e3), True, False, None=auto.
                indent          :Optional[Union[D,bool]] =Default,  # Indent for .deeper()
                color           :Optional[Union[D,bool]] =Default,  # ANSI colors in text
                deeper_width     :Optional[Union[D,int]] =Default): # For .deeper, how many entries to show per level

    "Set config variables"
    args = locals().copy()
    for k,v in args.items():
        if v != Default:
            if v is None:
                setattr(_config, k, getattr(_defaults, k))
            else:
                setattr(_config, k, v)

# %% ../../nbs/03_utils.config.ipynb 7
def get_config():
    "Get a copy of config variables"
    return copy(_config)

# %% ../../nbs/03_utils.config.ipynb 8
@contextmanager
def config( precision       :Optional[Union[D,int]]  =Default,  # Digits after `.`
            threshold_min   :Optional[Union[D,int]]  =Default,  # .abs() larger than 1e3 -> Sci mode
            threshold_max   :Optional[Union[D,int]]  =Default,  # .abs() smaller that 1e-4 -> Sci mode
            sci_mode        :Optional[Union[D,bool]] =Default,  # Sci mode (1.2e3), True, False, None=auto.
            indent          :Optional[Union[D,bool]] =Default,  # Indent for .deeper()
            color           :Optional[Union[D,bool]] =Default,  # ANSI colors in text
            deeper_width     :Optional[Union[D,int]] =Default): # For .deeper, how many entries to show per level

    "Context manager for temporarily setting printting options."
    global _config
    new_opts = { k:v for k, v in locals().items() if v != Default }
    old_opts = copy(get_config().__dict__)

    try:
        set_config(**new_opts)
        yield
    finally:
        set_config(**old_opts)
