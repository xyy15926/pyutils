# %%
import os
from typing import (Any, Union, Tuple)
CSS_DIR = os.path.join(__file__, "../../../resources/css")

# %%
LIGHT_COLORS = {
    "COLD": [
        '#1abc9c',
        '#16a085',
        '#2ecc71',
        '#27ae60',
        '#3498db',
        '#2980b9',
        '#34495e',
        '#2c3e50',
    ],
    "WARM": [
        '#9b59b6',
        '#8e44ad',
        '#f1c40f',
        '#f39c12',
        '#e67e22',
        '#d35400',
        '#e74c3c',
        '#c0392b',
    ],
    "GREY": [
        '#ecf0f1',
        '#bdc3c7',
        '#95a5a6',
        '#7f8c8d'
    ]
}
DEEP_COLORS = {
    "COLD": [
        '#0e6251',
        '#0b5345',
        '#186a3b',
        '#145a32',
        '#1b4f72',
        '#154360',
        '#1b2631',
        '#17202a',
    ],
    "WARM": [
        '#512e5f',
        '#4a235a',
        '#7d6608',
        '#7e5109',
        '#784212',
        '#6e2c00',
        '#78281f',
        '#641e16',
    ],
    "GREY": [
        '#7d7d7d',
        '#626567',
        '#4d5656',
        '#424949'
    ]
}

#%%
COLD_COLOR_LIST = [
    [
        '#0e6251',
        '#117864',
        '#148f77',
        '#17a589',
        '#1abc9c',
        '#48c9b0',
        '#76d7c4',
        '#a3e4d7',
        '#d1f2eb',
        '#e8f8f5'
    ],
    [
        '#0b5345',
        '#0e6655',
        '#117a65',
        '#138d75',
        '#16a085',
        '#45b39d',
        '#73c6b6',
        '#a2d9ce',
        '#d0ece7',
        '#e8f6f3'
    ],
    [
        '#186a3b',
        '#1d8348',
        '#239b56',
        '#28b463',
        '#2ecc71',
        '#58d68d',
        '#82e0aa',
        '#abebc6',
        '#d5f5e3',
        '#eafaf1'
    ],
    [
        '#145a32',
        '#196f3d',
        '#1e8449',
        '#229954',
        '#27ae60',
        '#52be80',
        '#7dcea0',
        '#a9dfbf',
        '#d4efdf',
        '#e9f7ef'
    ],
    [
        '#1b4f72',
        '#21618c',
        '#2874a6',
        '#2e86c1',
        '#3498db',
        '#5dade2',
        '#85c1e9',
        '#aed6f1',
        '#d6eaf8',
        '#ebf5fb'
    ],
    [
        '#154360',
        '#1a5276',
        '#1f618d',
        '#2471a3',
        '#2980b9',
        '#5499c7',
        '#7fb3d5',
        '#a9cce3',
        '#d4e6f1',
        '#eaf2f8'
    ],
    [
        '#1b2631',
        '#212f3c',
        '#283747',
        '#2e4053',
        '#34495e',
        '#5d6d7e',
        '#85929e',
        '#aeb6bf',
        '#d6dbdf',
        '#ebedef'
    ],
    [
        '#17202a',
        '#1c2833',
        '#212f3d',
        '#273746',
        '#2c3e50',
        '#566573',
        '#808b96',
        '#abb2b9',
        '#d5d8dc',
        '#eaecee'
    ]
]

WARM_COLOR_LIST = [
    [
        '#f9ebea',
        '#f2d7d5',
        '#e6b0aa',
        '#d98880',
        '#cd6155',
        '#c0392b',
        '#a93226',
        '#922b21',
        '#7b241c',
        '#641e16'
    ],
    [
        '#fdedec',
        '#fadbd8',
        '#f5b7b1',
        '#f1948a',
        '#ec7063',
        '#e74c3c',
        '#cb4335',
        '#b03a2e',
        '#943126',
        '#78281f'
    ],
    [
        '#fbeee6',
        '#f6ddcc',
        '#edbb99',
        '#e59866',
        '#dc7633',
        '#d35400',
        '#ba4a00',
        '#a04000',
        '#873600',
        '#6e2c00'
    ],
    [
        '#fdf2e9',
        '#fae5d3',
        '#f5cba7',
        '#f0b27a',
        '#eb984e',
        '#e67e22',
        '#ca6f1e',
        '#af601a',
        '#935116',
        '#784212'
    ],
    [
        '#fef5e7',
        '#fdebd0',
        '#fad7a0',
        '#f8c471',
        '#f5b041',
        '#f39c12',
        '#d68910',
        '#b9770e',
        '#9c640c',
        '#7e5109'
    ],
    [
        '#fef9e7',
        '#fcf3cf',
        '#f9e79f',
        '#f7dc6f',
        '#f4d03f',
        '#f1c40f',
        '#d4ac0d',
        '#b7950b',
        '#9a7d0a',
        '#7d6608'
    ],
    [
        '#f4ecf7',
        '#e8daef',
        '#d2b4de',
        '#bb8fce',
        '#a569bd',
        '#8e44ad',
        '#7d3c98',
        '#6c3483',
        '#5b2c6f',
        '#4a235a'
    ],
    [
        '#f5eef8',
        '#ebdef0',
        '#d7bde2',
        '#c39bd3',
        '#af7ac5',
        '#9b59b6',
        '#884ea0',
        '#76448a',
        '#633974',
        '#512e5f'
    ]
]

# %%
def get_colors_from_css(
    css_file: str
) -> Tuple[list, dict]:
    """
    Description:
    1. Get colors defined in css file

    Params:
    css_file: css file

    Return:
    color_list: list of base colors
    color_dict: {
        color-name: [derived-color-1, ]
    }
    """
    color_dict = {}
    color_list = []
    with open(css_file, "r") as fp:
        # for line contains color definition in css file
        _re_ptn = re.compile("\.([\w\-]+).*\{.*(#[0-9a-fA-F]{6,}).*\}.*")
        for line in fp:
            _cdef_matched = _re_ptn.match(line)
            if _cdef_matched:
                color_name, color_value = _cdef_matched.groups()
                # base-color: <name>
                # derived-color: <name>-<code>
                _cname_matched = re.match("([a-zA-z\-]+)-(\d+)", color_name)
                if _cname_matched:
                    base_name, derived_name = _cname_matched.groups()
                    _color_list = color_dict.setdefault(base_name, [])
                    _color_list.append(color_value)
                # for color-name with pattern: `[color_base]`
                else:
                    color_list.append(color_value)
    return color_list, color_dict

