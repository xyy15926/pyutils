#!  /usr/bin/env python3
#----------------------------------------------------------
#   Name: prompt.py
#   Author: xyy15926
#   Created at: 2019-05-05 00:15:40
#   Updated at: 2019-05-05 00:23:55
#   Description:
#----------------------------------------------------------
#%%
import sys
import time
import itertools as itl
import functools as ftl
import threading
import asyncio

#%%
class ProgressBar:
    """
    Description:
    Display progress bar on the console according to given
    total items and item done.

    Params:
    total:
    cur:
    msg: title of the progress bar
      - `\x08` default to backspace the last space
    lock: lock to ensure correct behavior in multi-thread
      situation
    """
    def __init__(self, total, cur=0, msg="\x08", lock=None):
        self.start_time = -1
        self.total = total
        self.cur = cur
        self.format = "{cur}/{total} {msg} [{bar}] {elapsed}"
        self.bar_len = 50
        self.msg = msg
        self.lock = lock
        if self.lock is True:
            self.lock = threading.Lock()

    def update(self, cur, msg=None):
        """
        Description:
        Update the number items done until now and print the
        progress bar

        Params:
        cur: the number of items done until now
        msg: title of the progress bar

        Return:
        """

        # acquire lock in multi-threads situation
        if self.lock:
            self.lock.acquire()

        self.cur = cur
        if msg:
            self.msg = msg
        if self.start_time == -1:
            self.start_time = time.time()

        # set bar format
        _percent = self.cur / self.total
        if _percent < 1:
            _bar = "=" * int(self.cur / self.total * self.bar_len) + ">" + \
                "-" * (self.bar_len - 1 - int(self.cur / self.total * self.bar_len))
        else:
            _bar = "=" * self.bar_len

        # set time format
        _time = int(time.time() - self.start_time)
        _time = "%02d:%02d" % (_time / 60, _time % 60)

        print(self.format.format(
            cur = self.cur,
            total = self.total,
            msg = self.msg,
            bar = _bar,
            elapsed = _time
        ), end="\r")

        if self.lock:
            self.lock.release()

    def incr(self, incr=1):
        """
        Description:
        Update the number of items done until now with
        increasment `incr`

        Params:
        incr:
        """
        self.update(self.cur+incr)

    def start(self):
        """
        Description:
        Start progress bar mannually, which may get more precise
        time count
        """
        self.start_time = time.time()
        self.update(0)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exec_type, exec_value, traceback):
        pass

#%%
ANSI_CSI_PREFIX = "\x1b["
ANSI_CSI_SGR = "m"
ANSI_CSI_SGR_RESET = "\x1b[0m"
ANSI_CSI_SGR_SPLIT = ";"
# format: [fg, bg]
ANSI_CSI_SGR_STYLE = {
    "highlight": ["1", "22"],
    "lowlight": ["2", "22"],
    "underline": ["4", "24"],
    "flash": ["5", "25"],
    "reverse": ["7", "27"],
    "hidden": ["8", "28"],
    "del": ["9", "29"],
}
# format: [fg, bg]
ANSI_CSI_SGR_16 = {
    "black": ["30", "40"],
    "hblock": ["90", "100"],
    "red": ["31", "41"],
    "hred": ["91", "101"],
    "green": ["32", "42"],
    "hgreen": ["92", "102"],
    "yellow": ["33", "43"],
    "hyellow": ["93", "103"],
    "blue": ["34", "44"],
    "hblue": ["94", "104"],
    "purple": ["35", "45"],
    "hpurple": ["95", "105"],
    "cyan": ["36", "46"],
    "hcyan": ["96", "106"],
    "white": ["37", "47"],
    "hwhite": ["97", "107"]
}
ANSI_CSI_SGR_256_FG = "38;5"
ANSI_CSI_SGR_256_BG = "48;5"
ANSI_CSI_SGR_RGB_FG = "38;2"
ANSI_CSI_SGR_RGB_BG = "48:2"

def colorize_16(msg, fg=None, bg=None, style=None):
    """
    Description:
    Colorize `msg` to display in terminal with 3/4 colors

    Params:
    msg:
    fg: forwardground color, selected from `ANSI_CSI_SGR_16`
    bg: background color, selected from `ANSI_CSI_SGR_16`
    style:

    Return:
    colorized `msg`
    """
    _fg = ANSI_CSI_SGR_16.get(fg, [""] * 2)[0]
    _bg = ANSI_CSI_SGR_16.get(bg, [""] * 2)[1]
    _sty = ANSI_CSI_SGR_STYLE.get(style, [""] * 2)[0]
    _joined = ";".join([_fg, _bg, _sty]).strip(";")
    return f"{ANSI_CSI_PREFIX}{_joined}{ANSI_CSI_SGR}{msg}{ANSI_CSI_SGR_RESET}"

def colorize_256(msg, fg=None, bg=None, style=None):
    """
    Description:
    Colorize `msg` to display in terminal with 256 colors

    Params:
    msg:
    fg: forwardground color, 0-255
    bg: background color, 0-255
    style:

    Return:
    colorized `msg`
    """
    _fg = f"{ANSI_CSI_SGR_256_FG};{str(fg)}" if fg else ""
    _bg = f"{ANSI_CSI_SGR_256_BG};{str(bg)}" if bg else ""
    _sty = ANSI_CSI_SGR_STYLE.get(style, [""] * 2)[0]
    _joined = ";".join([_fg, _bg, _sty]).strip(";")
    return f"{ANSI_CSI_PREFIX}{_joined}{ANSI_CSI_SGR}{msg}{ANSI_CSI_SGR_RESET}"

#%%
if __name__ == "__main__":
    # PROGRESSBAR TEST
    # with ProgressBar(100, msg="AHA", lock=True) as b:
    #     for i in range(100):
    #         b.incr()
    #         time.sleep(0.05)

    a = colorize_16("kaka", "cyan", "blue", "underline")
    b = colorize_256("kaka", 5)

#%%




