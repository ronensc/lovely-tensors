# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_repr_str.ipynb.

# %% auto 0
__all__ = ['lovely']

# %% ../nbs/00_repr_str.ipynb 3
from typing import Optional, Union
from collections import defaultdict
import warnings
import torch
from lovely_numpy.utils import np_to_str_common, pretty_str, sparse_join, plain_repr, PRINT_OPTS

# %% ../nbs/00_repr_str.ipynb 6
def type_to_dtype(t: str) -> torch.dtype:
    "Convert str, e.g. 'float32' to torch.dtype e.g torch.float32"
    
    dtp = vars(torch)[t]
    assert isinstance(dtp, torch.dtype)
    return dtp


# %% ../nbs/00_repr_str.ipynb 8
dtnames = { type_to_dtype(k): v
                for k,v in {"float32": "",
                            "float16": "f16",
                            "float64": "f64",
                            "uint8": "u8", # torch does not have uint16/32/64
                            "int8": "i8",
                            "int16": "i16",
                            "int32": "i32",
                            "int64": "i64",
                        }.items()
}

def short_dtype(x): return dtnames.get(x.dtype, str(x.dtype)[6:])

# %% ../nbs/00_repr_str.ipynb 10
@torch.no_grad()
def to_str(t: torch.Tensor,
            plain: bool=False,
            verbose: bool=False,
            depth=0,
            lvl=0,
            color=None) -> str:

    if plain:
        return plain_repr(t)

    tname = "tensor" if type(t) is torch.Tensor else type(t).__name__.split(".")[-1]
    shape = str(list(t.shape)) if t.ndim else None
    type_str = sparse_join([tname, shape], sep="")
    
    dev = str(t.device) if t.device.type != "cpu" else None
    dtype = short_dtype(t)
    grad_fn = t.grad_fn.name() if t.grad_fn else None
    # PyTorch does not want you to know, but all `grad_fn``
    # tensors actuall have `requires_grad=True`` too.
    grad = "grad" if t.requires_grad else None 
    

    # Done with collecting torch-specific info. Pass it to Lovely-Numpy
    common=None
    vals=None
    if not t.is_complex():
        common = np_to_str_common(t.cpu().numpy(), color=color, ddof=1)
        vals = pretty_str(t.cpu().numpy()) if t.numel() <= 10 else None

    res = sparse_join([type_str, dtype, common, grad, grad_fn, dev, vals])

    if verbose or t.is_complex():
        res += "\n" + plain_repr(t)

    if depth and t.dim() > 1:
        res += "\n" + "\n".join([
            " "*PRINT_OPTS.indent*(lvl+1) +
            str(StrProxy(t[i,:], depth=depth-1, lvl=lvl+1))
            for i in range(t.shape[0])])

    return res

# %% ../nbs/00_repr_str.ipynb 11
def history_warning():
    "Issue a warning (once) ifw e are running in IPYthon with output cache enabled"

    if "get_ipython" in globals() and get_ipython().cache_size > 0:
        warnings.warn("IPYthon has its output cache enabled. See https://xl0.github.io/lovely-tensors/history.html")

# %% ../nbs/00_repr_str.ipynb 14
class StrProxy():
    def __init__(self, t: torch.Tensor, plain=False, verbose=False, depth=0, lvl=0, color=None):
        self.t = t
        self.plain = plain
        self.verbose = verbose
        self.depth=depth
        self.lvl=lvl
        self.color=color
        history_warning()
    
    def __repr__(self):
        return to_str(self.t, plain=self.plain, verbose=self.verbose,
                      depth=self.depth, lvl=self.lvl, color=self.color)

    # This is used for .deeper attribute and .deeper(depth=...).
    # The second onthe results in a __call__.
    def __call__(self, depth=1):
        return StrProxy(self.t, depth=depth)

# %% ../nbs/00_repr_str.ipynb 15
def lovely(t: torch.Tensor, # Tensor of interest
            verbose=False,  # Whether to show the full tensor
            plain=False,    # Just print if exactly as before
            depth=0,        # Show stats in depth
            color=None):    # Force color (True/False) or auto.
    return StrProxy(t, verbose=verbose, plain=plain, depth=depth, color=color)
