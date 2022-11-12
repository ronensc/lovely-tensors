# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_repr_str.ipynb.

# %% auto 0
__all__ = ['PRINT_OPTS', 'pretty_str', 'lovely']

# %% ../nbs/00_repr_str.ipynb 3
from typing import Optional, Union
from collections import defaultdict
import torch

# %% ../nbs/00_repr_str.ipynb 4
class __PrinterOptions(object):
    precision: int = 3
    threshold_max: int = 3 # .abs() larger than 1e3 -> Sci mode
    threshold_min: int = -4 # .abs() smaller that 1e-4 -> Sci mode
    sci_mode: Optional[bool] = None # None = auto. Otherwise, force sci mode.
    indent: int = 2 # Indent for .deeper()
    color: bool = True

PRINT_OPTS = __PrinterOptions()

# %% ../nbs/00_repr_str.ipynb 5
# Do we want this float in decimal or scientific mode?
def sci_mode(f: float):
    return (abs(f) < 10**(PRINT_OPTS.threshold_min) or
            abs(f) > 10**PRINT_OPTS.threshold_max)

# %% ../nbs/00_repr_str.ipynb 8
# Convert a tensor or scalar into a string.
# This only looks good for small tensors, which is how it's intended to be used.
def pretty_str(t: Union[torch.Tensor, float, int]):
    """A slightly better way to print `float`-y values"""

    if isinstance(t, int):
        return '{}'.format(t)
    elif isinstance(t, float):
        if t == 0.:
            return "0."

        sci = (PRINT_OPTS.sci_mode or
                (PRINT_OPTS.sci_mode is None and sci_mode(t)))
        # The f-string will generate something like "{.4f}", which is used
        # to format the value.
        return f"{{:.{PRINT_OPTS.precision}{'e' if sci else 'f'}}}".format(t)
    elif t.dim() == 0:
            return pretty_str(t.item())
    else:
        slices = [pretty_str(t[i]) for i in range(0, t.size(0))]
        return '[' + ", ".join(slices) + ']'

# %% ../nbs/00_repr_str.ipynb 13
def space_join(lst):
    # Join non-empty list elements into a space-sepaeated string
    return " ".join( [ l for l in lst if l] )

# %% ../nbs/00_repr_str.ipynb 15
def type_to_dtype(t: str) -> torch.dtype:
    "Convert str, e.g. 'float32' to torch.dtype e.g torch.float32"
    
    dtp = vars(torch)[t]
    assert isinstance(dtp, torch.dtype)
    return dtp


# %% ../nbs/00_repr_str.ipynb 17
dtnames = { type_to_dtype(k): v
                for k,v in {"float32": "",
                            "float16": "f16",
                            "float64": "f64",
                            "uint8": "u8", # torch does not have uint16/32/64
                            "int8": "i8",
                            "int16": "i16",
                            "int32": "i32",
                            "int64": "i64",
                            "complex32": "c32",
                            "complex64": "c64",
                            "complex128": "c128",
                        }.items()
}

def short_dtype(x): return dtnames.get(x.dtype, str(x.dtype)[6:])

# %% ../nbs/00_repr_str.ipynb 19
def plain_repr(x: torch.Tensor):
    "Pick the right function to get a plain repr"
    assert isinstance(x, torch.Tensor) # Could be a sub-class.
    return x._plain_repr() if hasattr(type(x), "_plain_repr") else repr(x)

def plain_str(x):
    "Pick the right function to get a plain str"
    assert isinstance(x, torch.Tensor)
    return x._plain_str() if hasattr(type(x), "_plain_str") else str(x)

# %% ../nbs/00_repr_str.ipynb 20
def ansi_color(s: str, col: str, use_color=True):
        "Very minimal ANSI color support"
        style = defaultdict(str)
        style["grey"] = "\x1b[38;2;127;127;127m"
        style["red"] = "\x1b[31m"
        end_style = "\x1b[0m"
       
        return style[col]+s+end_style if use_color else s

# %% ../nbs/00_repr_str.ipynb 23
@torch.no_grad()
def to_str(t: torch.Tensor,
            plain: bool=False,
            verbose: bool=False,
            depth=0,
            lvl=0,
            color=None) -> str:

    if plain or t.is_complex():
        return plain_repr(t)

    color = PRINT_OPTS.color if color is None else color
    
    tname = "tensor" if type(t) is torch.Tensor else type(t).__name__
    dev = str(t.device) if t.device.type != "cpu" else None
    dtype = short_dtype(t)
    grad_fn = t.grad_fn.name() if t.grad_fn else None
    # PyTorch does not want you to know, but all `grad_fn``
    # tensors actuall have `requires_grad=True`` too.
    grad = "grad" if t.requires_grad else None 


    # Later, we might be indexing 't' with a bool tensor derived from it. 
    # THis takes 4x memory and will result in a CUDA OOM if 't' is very large.
    # Move it to the cpu now - it won't matter for small tensors, and for
    # very large ones we trade a CUDA OOM for a few seconds delay.
    t = t.detach().cpu()

    shape = str(list(t.shape))

    zeros = ansi_color("all_zeros", "grey", color) if t.eq(0.).all() and t.numel() > 1 else None
    pinf = ansi_color("+Inf!", "red", color) if t.isposinf().any() else None
    ninf = ansi_color("-Inf!", "red", color) if t.isneginf().any() else None
    nan = ansi_color("NaN!", "red", color) if t.isnan().any() else None

    attention = space_join([zeros,pinf,ninf,nan])

    numel = f"n={t.numel()}" if t.numel() > 5 and max(t.shape) != t.numel() else None
    summary = None
    vals = None
    if not zeros:
        if t.numel() <= 10: vals = pretty_str(t)
        
        # Make sure it's float32.
        # Also, we calculate stats on good values only.
        ft = t[ torch.isfinite(t) ].float()

        minmax = f"x∈[{pretty_str(ft.min())}, {pretty_str(ft.max())}]" if ft.numel() > 2 else None
        meanstd = f"μ={pretty_str(ft.mean())} σ={pretty_str(ft.std())}" if ft.numel() >= 2 else None

        summary = space_join([numel, minmax, meanstd])

    res = tname + space_join([  shape,
                                summary,
                                dtype,
                                grad,
                                grad_fn,
                                dev,
                                attention,
                                vals if not verbose else None])

    if verbose:
        res += "\n" + plain_repr(t)

    if depth and t.dim() > 1:
        res += "\n" + "\n".join([
            " "*PRINT_OPTS.indent*(lvl+1) +
            str(StrProxy(t[i,:], depth=depth-1, lvl=lvl+1))
            for i in range(t.shape[0])])

    return res

# %% ../nbs/00_repr_str.ipynb 24
class StrProxy():
    def __init__(self, t: torch.Tensor, plain=False, verbose=False, depth=0, lvl=0, color=None):
        self.t = t
        self.plain = plain
        self.verbose = verbose
        self.depth=depth
        self.lvl=lvl
        self.color=color
    
    def __repr__(self):
        return to_str(self.t, plain=self.plain, verbose=self.verbose,
                      depth=self.depth, lvl=self.lvl, color=self.color)

    # This is used for .deeper attribute and .deeper(depth=...).
    # The second onthe results in a __call__.
    def __call__(self, depth=0):
        return StrProxy(self.t, depth=depth)

# %% ../nbs/00_repr_str.ipynb 26
def lovely(t: torch.Tensor, # Tensor of interest
            verbose=False,  # Whether to show the full tensor
            plain=False,    # Just print if exactly as before
            depth=0,        # Show stats in depth
            color=None):    # Force color (True/False) or auto.
    return StrProxy(t, verbose=verbose, plain=plain, depth=depth, color=color)
