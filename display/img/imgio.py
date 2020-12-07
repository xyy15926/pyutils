# %%
import imageio
import cv2
import os
import time
import logging
import numpy as np 
logger = logging.getLogger(f"main.{__name__}")
from typing import (Any, Union, Tuple)
from . import (DYNAMIC, STATIC, PREDEF_COLORS)
from .imgils import (compress_image, color_str2num, color_num2str,
        strip_space, convert_png_black)

# %%
def save_ims(
    ims: list,
    file_name:str = "",
    file_type:str = "",
    to_strip_space:bool = True,
    to_compress:bool = True,
    ignore_exists:bool = True,
    **kwargs
) -> None:
    """
    Description:
    Create image or video from `ims`

    Params:
    ims: list of str, bytes, file
    file_name:
    to_strip_space: if strip space in image
    to_compress: if compress image
    ignore_exists: whether to ignore existing file
        True: replace existing file
        False: save images with another name
    kwargs: keyword parameters that will be passed to `imageio.mimsave`

    Return:
    None
    """
    # Get or set name and filetype
    file_name = file_name or "gif.gif"
    file_type = (file_type or file_name.split(".")[-1]).lower()

    # Alter destinated filename if exists
    if not ignore_exists and os.path.exists(file_name):
        file_name_splited = file_name.split(".")
        file_name = "".join([
            *file_name_splited[:-1],
            f"_{int(time.time())}",
            *file_name_splited[-1:]
        ])

    # For dynamic file type, gif for example, save image
    # in one file
    if file_type in DYNAMIC:
        with imageio.get_writer(file_name, file_type, **kwargs) as writer:
            for im in ims:
                # `im`: np.ndarray, regarded as np.ndarray image in memory
                # `im`: str, file, bytes, read them into np.ndarray
                if not isinstance(im, np.ndarray):
                    im = imageio.imread(im)
                im = convert_png_black(im)
                if to_strip_space:
                    im = strip_space(im)
                if to_compress:
                    im = compress_image(im)
                writer.append_data(im)
    # For static file type, png for example
    elif file_type in STATIC:
        # Mkdir with name `file_name` if the number if image > 2
        if len(ims) > 1:
            if not os.path.isdir(file_name):
                os.mkdir(file_name)
            for idx, im in enumerate(ims):
                if not isinstance(im, np.ndarray):
                    im = imageio.imread(im)
                im = convert_png_black(im)
                imageio.imsave(
                    os.path.join(file_name, f"{idx}.{file_type}"),
                    im,
                    **kwargs
                )
        # Save image directly
        else:
            im = imageio.imread(ims[0])
            imageio.imsave(
                file_name,
                im,
                **kwargs
            )
    else:
        logger.warning(f"Unrecogized file type {file_type}")

# %%
def save_video():
    pass