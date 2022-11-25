# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_repr_rgb.ipynb.

# %% auto 0
__all__ = ['rgb']

# %% ../nbs/01_repr_rgb.ipynb 4
from PIL import Image
import torch

from lovely_numpy.utils.pad import pad_frame_gutters
from lovely_numpy.utils.tile2d import hypertile
from lovely_numpy import rgb as np_rgb

# %% ../nbs/01_repr_rgb.ipynb 5
def rgb(t: torch.Tensor, # Tensor to display. [[...], C,H,W] or [[...], H,W,C]
            denorm=None, # Reverse per-channel normalizatoin
            cl=False,    # Channel-last
            gutter_px = 3,  # If more than one tensor -> tile with this gutter width
            frame_px=1,  # If more than one tensor -> tile with this frame width
            scale=1,
            view_width=966): # targer width of the image
     
    return np_rgb(t.detach().cpu().numpy(),
                    denorm=denorm, cl=cl, gutter_px=gutter_px,
                    frame_px=frame_px, scale=scale,
                    view_width=view_width)

# %% ../nbs/01_repr_rgb.ipynb 6
# This is here for the monkey-patched tensor use case.

# I want to be able to call both `tensor.rgb` and `tensor.rgb(stats)`. For the
# first case, the class defines `_repr_png_` to send the image to Jupyter. For
# the later case, it defines __call__, which accps the argument.

class RGBProxy():
    """Flexible `PIL.Image.Image` wrapper"""
    
    def __init__(self, t:torch.Tensor):
        # super().__init__()
        assert t.ndim >= 3, f"Expecting at least 3 dimensions, got shape{t.shape}={t.dim()}"
        self.t = t #.detach().cpu().numpy()

    def __call__(   self,
                    denorm=None,
                    cl=False,
                    gutter_px=3, frame_px=1,
                    scale=1,
                    view_width=966):

        return rgb(self.t, denorm=denorm, cl=cl, gutter_px=gutter_px,
                frame_px=frame_px, view_width=view_width)
    
    @torch.no_grad()
    def _repr_png_(self):
        # Note: In order to prevernt IPYthon from hogging memory, we
        # delete the reference to the tensor after the first call to
        # `_repr_png_`. This is fine for Jupyter use.
        return self.__call__()._repr_png_()

