# %%
from typing import (Any, Union, Tuple)
from pyecharts.charts import (Grid, Line, Bar)
import pyecharts.options as opts
from ..colors import (LIGHT_COLORS, DEEP_COLORS, WARM_COLOR_LIST, 
                      COLD_COLOR_LIST)

# %%
def draw_roc(
    fpr:list,
    tpr:list,
    area_color:list=[],
    is_show_ks:bool=True,
    title:str="ROC"
) -> Line:
    """
    Description:
    1. Draw roc

    Params:
    fpr
    tpr
    area_color: [area_under_yx, area_under_curve]
    is_show_ks
    title

    Return:
    None
    """
    area_color = area_color or [LIGHT_COLORS["COLD"][3], LIGHT_COLORS["WARM"][5]]
    # Draw roc
    line = Line().add_xaxis(fpr)
    line.add_yaxis(
        "",
        tpr,
        is_smooth=True,
        areastyle_opts=opts.AreaStyleOpts(
            opacity=0.5,
            color=area_color[1],
        ),
        label_opts=opts.LabelOpts(
            is_show=None
        ),
        color=area_color[1],
        symbol_size=0,
    )
    line.add_yaxis(
        "",
        fpr,
        is_smooth=True,
        areastyle_opts=opts.AreaStyleOpts(
            opacity=0.5,
            color=area_color[0],
        ),
        label_opts=opts.LabelOpts(
            is_show=None
        ),
        color=area_color[1],
        symbol_size=0,
    )
    line.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            pos_left="center"
        ),
        xaxis_opts=opts.AxisOpts(
            type_="value",
            name="FPR"
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="TPR"
        ),
        toolbox_opts=opts.ToolboxOpts()
    )
    if is_show_ks:
        line.set_series_opts(
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(
                        name="KS",
                        type_="value",
                        x=max(zip(tpr-fpr, fpr))[1],
                    )
                ]
            )
        )
    return line

# %%
def draw_hist(
    nums:list,
    bins:list,
    title:str="",
    font_size:int=13
) -> Bar:
    """
    Description:
    1. draw histogram

    Params:
    bins: edge of each bin
    nums: MUST BE LIST. IF np.ndarray PASSED, BAR CAN'T BE RENDERED
        CORRECTLY
    title

    Return:
    bar
    """
    bins = list(zip(bins[:-1], bins[1:]))
    bar = Bar().add_xaxis(bins)
    bar.add_yaxis(
        "",
        nums,
        category_gap=0,
        is_clip=False
    )
    bar.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(
                interval=0,
                font_size=font_size,
                rotate=90
            ),
        ),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(
                font_size=font_size,
            ),
        ),
        title_opts=opts.TitleOpts(
            title=None
        )
    )
    return bar

# %%
