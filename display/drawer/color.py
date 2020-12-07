#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: color.py
#   Author: xyy15926
#   Created at: 2020-11-12 20:49:29
#   Updated at: 2020-11-12 20:50:21
#   Description: Contains some pre-defined colors, colormap, etc
#----------------------------------------------------------

# %%
import os
import re
import matplotlib as mpl
from ..colors import (get_colors_from_css, LIGHT_COLORS, DEEP_COLORS,
                      WARM_COLOR_LIST, COLD_COLOR_LIST)
CSS_DIR = os.path.join(__file__, "../../../resources/css")

# %% [markdown]
# Generate Colormap

# %%
def gen_cmaps() -> dict:
    """
    Description:
    Generate color maps with color-list get from all
    channels
    1. `get_colors_from_css`

    Params:
    None

    Return:
    cmaps
    """
    cmaps = {}

    # Generate cmaps from css
    css_dir = CSS_DIR
    css_files = os.listdir(css_dir)
    for css_file in css_files:
        _, cdict = get_colors_from_css(os.path.join(css_dir, css_file))
        cmaps.update({
            cname: mpl.colors.LinearSegmentedColormap.from_list(cname, clist) \
                for cname, clist in cdict.items()
        })

    # Generate cmaps from predefined color-list
    for idx, (cold_list, warm_list) in enumerate(zip(COLD_COLOR_LIST, WARM_COLOR_LIST)):
        cname, rname = f"cpair_{idx}", f"rpair_{idx}"
        clist = cold_list + warm_list
        cmaps[cname] = mpl.colors.LinearSegmentedColormap.from_list(cname, clist)
        cmaps[rname] = mpl.colors.LinearSegmentedColormap.from_list(cname, list(reversed(clist)))

    return cmaps

# %%
def plot_examples(colormaps) -> None:
    """
    Description:
    Helper function to plot data with associated colormap.

    Params:
    colormaps:

    Return:
    None
    """
    import numpy as np
    import matplotlib.pyplot as plt
    np.random.seed(19680801)
    data = np.random.randn(30, 30)
    n = len(colormaps)
    fig, axs = plt.subplots(int(np.sqrt(n)), int(np.ceil(n // int(np.sqrt(n)))), figsize=(n * 2 + 2, 3),
                            constrained_layout=True, squeeze=False)
    for [ax, cmap] in zip(axs.flat, colormaps):
        psm = ax.pcolormesh(data, cmap=cmap, rasterized=True, vmin=-4, vmax=4)
        fig.colorbar(psm, ax=ax)
    plt.savefig("color_map.png")


# %%
if __name__ == "__main__":
    cmaps = gen_cmaps()
    plot_examples(cmaps.values())

