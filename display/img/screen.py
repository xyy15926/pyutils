# %%
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

# %%
def screen_grab(
    file_name:str,
    fps:int=24,
    delay:float=2
) -> None:
    im = ImageGrab.grab()
    width, height = im.size
    k = np.zeros((200, 200), np.uint8)
    fourcc = cv2.VideoWriter_fourcc(*"U263")
    video = cv2.VideoWriter(file_name, fourcc, fps // 2, (width, height))
    while True:
        im = ImageGrab.grab()
        im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        video.write(im)
        cv2.imshow("ka", k)
        if cv2.waitKey(1000 // fps * 2) & 0xFF == ord("q"):
            break
    video.release()
    cv2.destroyAllWindows()

# %%
