#%%
from PIL import ImageGrab
import imageio
import cv2
import os
import time
import logging
import numpy as np 
logger = logging.getLogger(f"main.{__name__}")
from typing import (Any, Union, Tuple)
from . import (DYNAMIC, STATIC, PREDEF_COLORS)


#%%
def compress_image(
    im:np.ndarray,
    max_:int=1000000
) -> np.ndarray:
    """
    Description:
    1. Compress image's size lower than `max_`

    Params:
    im: image represented by np.ndarray
    max_: max size

    Return:
    compressed image
    """
    im_shape = list(im.shape)
    while im_shape[0] * im_shape[1] > max_:
        im_shape[0], im_shape[1] = im_shape[0] // 2, im_shape[1] // 2
    im = cv2.resize(im, (im_shape[1], im_shape[0]))
    return im

# %%
def color_str2num(
    cstr: str
) -> tuple:
    """
    Description:
    1. Convert color string expression, "#11AACC" for example, into
        tuple with 3 integers representing RGB channels

    Params:
    cstr: color string

    Return:
    """
    cstr = cstr.strip("# ")
    r, g, b = int(cstr[:2], 16), int(cstr[2: 4], 16), int(cstr[4:], 16)
    return r, g, b
def color_num2str(
    r: int,
    g: int,
    b: int
) -> str:
    """
    Description:
    1. Convert color tuple representing RGB 3 channels with 3 integers into 
    color string expression, "#11AACC" for example, into
        tuple with 3 integers representing RGB channels

    Params:
    cstr: color string

    Return:
    """
    return ("%02x%02x%02x" % (r, g, b)).upper()

#%%
def strip_space(
    im: np.ndarray,
    target:Union[str, tuple] = "white",
    how:str = "margin"
) -> np.ndarray:
    """
    Description:
    Strip stripe with specific color 

    Params:
    im
    target: target color, represented by str or tuple of number
    how: how to strip
        "margin": only stripe at margin will be striped
        "all": all stripe will be striped

    Return:
    im
    """

    # Set target and mask
    assert(len(im.shape) == 3)
    im_mask = im[:, :, :3]
    if isinstance(target, str):
        _target = PREDEF_COLORS.get(target)
        _target = _target or color_str2num(target)
    else:
        _target = target

    # Strip target
    if how == "margin":
        # Record range of tranparent rows
        for row_start in range(im.shape[0]):
            if (im_mask[row_start, :, :] != _target).any():
                break
        for row_end in range(im.shape[0]-1, row_start-1, -1):
            if (im_mask[row_end, :, :] != _target).any():
                break
        row_end += 1

        # Record range of tranparent cols
        for col_start in range(im.shape[1]):
            if (im_mask[:, col_start, :] != _target).any():
                break
        for col_end in range(im.shape[1]-1, -1, -1):
            if (im_mask[:, col_end, :] != _target).any():
                break
        col_end += 1
        return im[row_start: row_end, col_start: col_end, :]
    elif how == "all":
        im = im[(im_mask != _target).any(1).any(1), :, :][:, (im_mask != _target).any(0).any(1), :]
        return im
    else:
        logger.warning(f"Unrecognized parameter for `how`: {how}")

# %%
def convert_png_black(im):
    """
    Description:
    1. Convert transparent black pixels into trasnparent white pixels,
        a.k.a (0, 0, 0, 0) -> (255, 255, 255, 0)

    Params:
    im: image with format of np.ndarray

    Return:
    """
    im[:,:,:3][(im == 0).all(2)] = 255 
    return im

# %%
def add_opacity():
    pass

#%%
if __name__ == "__main__":
    gif_path = "C:/Users/Administrator/Desktop/giftmp"
    ims = [os.path.join(gif_path, i) for i in os.listdir(gif_path)]
    create_gif(ims, "ka.gif")
