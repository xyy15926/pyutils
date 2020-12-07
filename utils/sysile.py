#!  /usr/bin/env python3
#----------------------------------------------------------
#   Name: log.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:58:23
#   Updated at: 2020-09-07 18:58:26
#   Description:
#----------------------------------------------------------

#%%
import os

#%%
def get_file_with_ext(directory, exts=[".csv", ".xls", ".xlsx"]):
    """
    Description:
    Get files with specified extension names

    Params:
    directory:
    exts: list of extension names

    Return:
    list of files with specified extension names
    """
    rets = []
    for root, dirs, files in os.walk(directory):
        for _file in files:
            if os.path.splitext(_file)[-1] in exts:
                rets.append(os.path.join(root, _file))
    return rets


#%%
