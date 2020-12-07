#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: __init__.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:55:16
#   Updated at: 2020-09-07 18:55:19
#   Description: top `__init__.py` contains all kinds of
#     settings for the whole package
#----------------------------------------------------------
#%%
import os
import datetime
import logging
import functools as ftl
import numpy as np
import matplotlib.pyplot as plt

#%%
logger = logging.getLogger("xutils.drawer")
# setup matplotlib if exists
def _setup_plt():
    _linux_font = "WenQuanYi Micro Hei Mono"
    _ms_font = "Microsoft Yahei"
    plt.rcParams["font.sans-serif"].insert(0, _ms_font)
    plt.rcParams["font.sans-serif"].insert(0, _linux_font)
    plt.rcParams["axes.unicode_minus"] = False
    plt.style.use("tableau-colorblind10")
_setup_plt()

def _setup_echarts():
    pass

TODAY = datetime.date.strftime(datetime.date.today(), "%Y%m%d")
NOW = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d %H%M%S")

#%%
def axit(func=None, *,fig_name="fig"):
    """
    Description:
    1. set `ax` for `func`
    2. save figure with `fig_name` in `dpath` or current curdir

    Parameters:
    func: functions to draw
    fig_name:

    Return:
    """
    # use `partial` to avoid another wrapper
    if not func:
        return ftl.partial(axit, fig_name=fig_name)
    @ftl.wraps(func)
    def wrapper(*args, **kwargs):
        # if `ax` in parameters, get a new ax in new figure
        ax = kwargs.setdefault("ax", plt.figure().add_subplot(111))

        # do something here
        _ret = func(*args, **kwargs)

        # if `dpath` in parameters, save figure
        dpath = kwargs.setdefault("dpath", ".")
        logger.info("figure(s) will be saved in `%s`", dpath)
        plt.gcf().savefig(os.path.join(dpath, f"{fig_name}_{TODAY}_.png"))
        return _ret

    return wrapper

#%%
@axit(fig_name="roc_curve")
def draw_roc(fpr, tpr, thd, *, ax=None):
    """
    Description:
    draw ROC curve

    Params:
    fpr: false positive rate
    tpr: true positive rate
    thd: threshholds for fpr, tpr
    ax: axes to draw, `plt.gca` as default

    Return:
    """
    ax = ax or plt.gca()
    ax.plot(fpr, tpr, linestyle="-")
    ax.plot(np.arange(0, 1.01, 0.05), np.arange(0, 1.01, 0.05), linestyle="--")
    ax.set_title("ROC Curve")
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")

# draw_roc(fpr, tpr, thd)
#%%
@axit(fig_name="ks_curve")
def draw_ks(fpr, tpr, thd, *, ax=None):
    """
    Description:
    draw KS curve

    Params:
    fpr: false positive rate
    tpr: true positive rate
    thd: threshholds for fpr, tpr
    ax: axes to draw, `plt.gca` as default

    Return:
    """
    ax = ax or plt.gca()
    ks_idx = (tpr - fpr).argmax()
    ax.plot(thd, tpr)
    ax.plot(thd, fpr)
    ax.plot(thd, tpr - fpr)
    ax.vlines(thd[ks_idx], tpr[ks_idx], fpr[ks_idx])
    ax.set_xlim(ax.get_xlim()[::-1])
    ax.legend(["TPR", "FPR", "KS"])
    ax.set_xlabel("Scores")
    ax.set_ylabel("Frequency")
    ax.set_title("KS Curve")

# draw_ks(fpr, tpr, thd)
#%%
@axit(fig_name="bar_line")
def draw_bar_line(bars, lines, stops, ascending=False,
    *, ax=None):
    """
    Description:

    Params:
    bars:
    lines:
    stops:

    Return:

    """

    # if no axessubplot is specified, get current ax
    ax = ax or plt.gca()

    # draw bars
    if bars:
        width = stops[1:] - stops[:-1]
        bottom = np.zeros(len(bars[0]))
        for y in bars:
            ax.bar(stops[:-1], y, width, bottom=bottom, align="edge")
            bottom += y

    # draw lines
    if lines:
        sym_ax = ax.twinx()
        for y in lines:
            sym_ax.plot(stops[:-1], y, linestyle="-.")

    # check if need to reverse xlim
    if not ascending:
        ax.set_xlim(ax.get_xlim()[::-1]) 
 
# draw_bar_line([df_grouped["g_cnt"], df_grouped["b_cnt"]], [df_grouped["cum_b_ratio"]], stops)
# draw_bar_line([], [df_grouped["cum_b_ratio"]], stops)

# %%
if __name__ == "__main__":
    tgt = np.array([0]*10 + [1]*10)
    tgt[15] = 0
    score = np.linspace(0, 1, 20)
    stops = np.linspace(0, 1, 4)
    fpr, tpr, thd = sklm.roc_curve(tgt, score)
    thd[0] = thd[1] * (1+1e-7)

# %%
