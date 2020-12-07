# %%
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType
from pyecharts.faker import Faker

# %% [markdown]
# ## GLOBAL OPTIONS
INIT = {
    "imgbg": opts.InitOpts(
        width="100%",
        height="100%",
        theme=ThemeType.MACARONS,
        animation_opts=opts.AnimationOpts(
            animation_delay=1000,
            animation_easing="elasticOut"
        )
        bg_color={
            "type": "pattern",
            "image": JsCode("(img = new Image(); img.src='background.png'; img)"),
            "repeat": "center"
        }
    )
}
DATA_ZOOM = [
    opts.DataZoomOpts(
        is_show=False,
        type_="inside",
        is_realtime=False,
        xaxis_index=[0, 0],
        range_start=0,
        range_end=100,
    ),
    opts.DataZoomOpts(
        is_show=True,
        type_="slider",
        is_realtime=False,
        orient="horizontal",
        xaxis_index=0,
        is_zoom_lock=False
    ),
    opts.DataZoomOpts(
        is_show=True,
        type_="slider",
        is_realtime=False,
        orient="vertical",
        yaxis_index=0,
        is_zoom_lock=False
    )
]
TITLE= opts.TitleOpts(
    pos_top="40px",
    pos_left="center",
    title="TITLE",
    subtitle="SUBTITLE",
    title_textstyle_opts=txt_opts
)


# %%
# ## SERIES OPTIONS
# ### Explaination Options
TOOlTIP = {
    "click": opts.TooltipOpts(
        is_show=True,
        trigger="item",
        trigger_on="click",
        axis_pointer_type="shadow",
        formatter="名称：{a} <br/> {b}: {c}%"
    ),
    "mouse": opts.TooltipOpts(
        is_show=True,
        trigger="axis",
        trigger_on="mousemove",
        axis_pointer_type="cross",
        formatter="名称：{a} <br/> {b}: {c}%"
    ),
    "hidden": opts.TooltipOpts(
        is_show=False
    )
}
LABEL_OPTS = {
    "standard": opts.LabelOpts(
        is_show=True,
        position="left",
        font_size=12,
        color="#999999",
        font_family="Microsoft YaHei"
    ),
    "rich": opts.LabelOpts(
        is_show=True,
        position="outside",
        formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
        background_color="#eee",
        border_color="#aaa",
        border_width=1,
        border_radius=4,
        rich={
            "a": {"color": "#999", "lineHeight": 18, "align": "center"},
            "abg": {
                "backgroundColor": "#e3e3e3",
                "width": "100%",
                "align": "right",
                "height": 22,
                "borderRadius": [4, 4, 0, 0],
            },
            "hr": {
                "borderColor": "#aaa",
                "width": "100%",
                "borderWidth": 0.5,
                "height": 0,
            },
            "b": {"fontSize": 12, "lineHeight": 18},
            "per": {
                "color": "#eee",
                "backgroundColor": "#334455",
                "padding": [2, 4],
                "borderRadius": 2,
            }
        }
    )
}
LEGEND = {
    "single": opts.LegendOpts(
        is_show=True,
        selected_mode="single"
    ),
    "hidden": opts.LegendOpts(
        is_show=False
    )
}

# %% [markdown]
# ### Item Options
ITEM = {
    "standard": opts.ItemStyleOpts(
        color="#ec0000",
        color0="#00da3c",
        border_color="#8A00000",
        border_color0="#008F28"
    ),
    "value_depending": opts.ItemStyleOpts(
        color=JsCode(
"""
function(params){
    if(params.value > 0 && params.value < 50){
        return 'red';
    }else{
        return 'blue';
    }
}
"""
        )
    ),
    "value_depending_2": {
        "normal": {
            "color": JsCode(
"""
new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    {
        offset: 0,
        color: 'rgba(0, 244, 255, 1)'
    },{
        offset: 1,
        color: 'rgba(0, 77, 167, 1)'
    }
], false)
"""
            ),
            "barBorderRadius": [30, 30, 30, 30],
            "shadowColor": "rgb(0, 160, 221)"
        }
    }
}
GRAPH = {
    "text": lambda x: opts.GraphicText(
        graphic_item = opts.GraphicItem(
            left="center",
            top="center",
            z=100
        ),
        graphic_textstyle_opts = (
            text=x,
            font="bold 26px Microsoft Yahei",
            graphic_basicstyle_opts=opts.GraphicBacisStyleOpts(
                fill="#ffffff"
            )
        )
    ),
    "rect": opts.GraphicRect(
        graphic_item = opts.GraphicItem(
            left="center",
            top="center",
            z=100
        ),
        graphic_shape_opts=opts.GraphicShapeOpts(
            width=400,
            height=50
        ),
        graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
            fill="rgba(0, 0, 0, 0.3)"
        )
    ),
    "printer" = opts.GraphicGroup(
        rotation=JsCode("Math.PI / 4"),
        bounding="raw",
        right=110,
        bottom=110,
        z=100
    ),
    "children"=[GRAPH["rect"], GRAPH["text"]]
}


# %% [markdown]
# ### Style Options
TEXT = {
    "white": opts.TextStyleOpts(
        color="#ffffff"
    )
}
LINE = {
    "standard": opts.LineStyleOpts(
        color=[(0.3, "#67e0e3"), (0.7, "#37a2da"), (1, "#fd666d")],
        width=10,
    ),
    "source": opts.LineStyleOpts(
        color="source",
        width=10
    ),
    "curve": opts.LineStyleOpts(
        color="source",
        width=1,
        curve=0.3
        opacity=0.7,
    )
}
AREA = {
    "opaque": opts.AreaStyleOpts(
        opacity=1
    ),
    "glassy": opts.AreaStyleOpts(
        opacity=0.1
    )
}
SPLITAREA = {
    "opaque" = opts.SplitAreaOpts(
        is_show=True,
        areastyle_opts=opts.AreaStyleOpts(
            opacity=1
        )
    )
}

# %% [markdown]
# ### Utils Options
AXLINE = {
    "standard": opts.AxisLineOpts(
        linestyle_opts=LINE["standard"]
    )
}
ANGLEAX = {
    "value": opts.AngleAxisOpts(
        type_="value",
        boundary_gap=True,
        start_angle=90,
        is_clockwise=True,
        interval=90,
        max_=360
    ),
    "category": lambda x: opts.AngleAxisOpts(
        data=x,
        type_="category",
        boundary_gap=True,
        start_angle=0,
        is_clockwise=True
    )
}
RADIUSAX = {
    "value": opts.RadiusAxisOpts(
        type_="value",
        boundary_gap=True,
        max_=100
    ),
    "category": lambda x: opts.RadiusAxisOpts(
        data=x,
        type_="category",
        boundary_gap=True
    )
}
SINGLEAX = {
    "time": opts.SingleAxisOpts(
        pos_right=10,
        pos_top=50,
        pos_bottom=50,
        type_="time"
    )
}
