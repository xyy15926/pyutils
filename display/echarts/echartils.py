# %%
from functools import (partial, )
from typing import (Any, Union, Tuple)
from ..peteer.websnap import (run_snapshots, )
from ..img.imgio import (save_ims, )
from ...utils.dencode import decode_b64
import pyecharts
import pyecharts.options as opts
from pyecharts.charts import (Grid, )

PNG_FORMAT = "png"
JPG_FORMAT = "jpeg"
GIF_FORMAT = "gif"
PDF_FORMAT = "pdf"
SVG_FORMAT = "svg"
EPS_FORMAT = "eps"
B64_FORMAT = "base64"

# %%
def dict4sunb(dt: dict) -> list:
    """
    Description:
    Convert dict with structure
        ```
        {
            lv1_1:{
                lv_1_2_1: {
                    lv_1_2_3_1: value,
                }
            },
            lv1_2:{

            }
        }
        ```
    to dict with structure satisifies the sunburst
        ```
        [
            {
                name: lv1_1,
                children:[
                    {
                        name: lv2_1,
                        value:
                    }
                ]
            },
            {
                name: lv1_2,
                children:[

                ]
            }
        ]
        ```
    with recurrusion

    Params:
    dt: dict with structure mentioned before

    Return:
    list with structure mentioned before
    """
    ret = []
    for key_, val_ in dt.items():
        if isinstance(val_, dict):
            ret.append({"name": key_, "children": dict4sunb(val_)})
        else:
            ret.append({"name": key_, "value": val_})
    return ret

# %%
async def _snapshot(
    page: Any,
    file_type: str,
    pixel_ratio:int = 2
) -> str:
    """
    Description:
    Make snapshot in `page` with JS code defined in this function
    according to the filetype

    Params:
    page: webpage in pyppeteer
    file_type:
    pixel_ratio:

    Return:
    snapshot data
    """
    SNAPSHOT_JS = (
        "echarts.getInstanceByDom(document.querySelector('div[_echarts_instance_]'))."
        "getDataURL({type: '%s', pixelRatio: %s, excludeComponents: ['toolbox']})"
    )
    SNAPSHOT_SVG_JS = "document.querySelector('div[_echarts_instance_] div').innerHTML"

    # Generate js function
    if file_type == "svg":
        snapshot_js = SNAPSHOT_SVG_JS
    else:
        snapshot_js = SNAPSHOT_JS % (file_type, pixel_ratio)
    return await page.evaluate(snapshot_js)

async def make_snapshot(
    html_path: str,
    output_name: str,
    file_type:str = "",
    pixel_ratio: int = 2,
    delay: int = 0,
    snap_fps:int = 24,
    frame_n:int = 1,
    intervals:list = [],
    browser: Any = None,
    **kwargs
) -> None:
    # Get or set filetype
    file_type = (file_type or output_name.split(".")[-1]).lower()

    # Set snapshot function
    snapshot_partial = partial(
        _snapshot,
        file_type=file_type,
        pixel_ratio=pixel_ratio
    )

    # Await to get snapshots
    rets = await run_snapshots(
        html_path,
        snapshot_partial,
        delay,
        snap_fps,
        frame_n,
        intervals,
        browser,
        **kwargs
    )

    # Save snapshots result in file directly
    if file_type in [SVG_FORMAT, B64_FORMAT]:
        assert(len(rets) == 1)
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(rets[0])
    # Split image data from snapshot result and call function
    # to save them
    else:
        save_ims(
            [decode_b64(ret.split(",")[1]) for ret in rets],
            output_name,
            file_type,
            **kwargs
        )

# %%
def margin_chart(
    chart:pyecharts.charts.chart.Chart,
    margin:list=[]
) -> Grid:
    """
    Description:
    1. Arange `chart` in a grid to set the margin

    Params:
    chart
    margin: [top, left, bottom, right]

    Return:
    grid
    """
    margin = margin or [0, 0, 0, 0]
    grid = Grid()
    grid.add(
        chart,
        grid_opts=opts.GridOpts(
            pos_top = margin[0] or None,
            pos_left = margin[1] or None,
            pos_bottom = margin[2] or None,
            pos_right = margin[3] or None
        )
    )
    return grid

