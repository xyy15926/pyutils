# %%
import pandas as pd 
from typing import (Any, Union, Tuple)
from .openxl import (add_format, format_worksheet, format_excel, _get_col_str)


# %%
def save_as_excel(
    dfs: Union[list, dict],
    file_: Union[str, pd.io.excel._OpenpyxlWriter],
    names:list = [],
    **kwargs,
) -> pd.io.excel._OpenpyxlWriter:
    """
    Description:
    1. Save a list of dataframes in one excel workbook

    Params:
    dfs: list of dataframes, or {<sheetname>: df, } at which
        occasion `names` will be ignored
    names: sheet names
    file_: _OpenpyxlWriter or filename
    kwargs: keywork parameters for `.to_excel`
    """
    # Set sheetnames and dataframes
    if isinstance(dfs, dict):
        names = dfs.keys()
        dfs = dfs.values()
    else:
        names = names or [f"Sheet{idx}" for idx in range(1, len(dfs)+1)]
        assert(len(names) == len(dfs))

    # Set ExcelWriter
    if isinstance(file_, str):
        file_ = pd.ExcelWriter(file_, engine="openpyxl")
    add_format(file_.book)

    # Write dataframes to worksheets in `file_`
    startrow = kwargs.setdefault("startrow", 1)
    startcol = kwargs.setdefault("startcol", 1)
    for name, df in zip(names, dfs):
        df.to_excel(file_, name, **kwargs)
        row_index_width = len(getattr(df.index, "levshape", "1"))
        col_index_height = len(getattr(df.columns, "levshape", "1"))
        anchors = [
            f"{_get_col_str(startcol+1)}{startrow+1}",
            f"{_get_col_str(startcol+1+row_index_width)}{startrow+1+col_index_height}",
            ""
        ]
        format_worksheet(file_.book[name], anchors)

    return file_