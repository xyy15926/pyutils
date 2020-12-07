#!  /usr/bin/python3
#----------------------------------------------------------
#   Name: keras_tools.py
#   Author: xyy15926
#   Created at: 2019-01-14 00:17:57
#   Updated at: 2020-09-04 11:40:02
#   Description: 
#----------------------------------------------------------

#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#%%
def df_shift_lag(df, lag=1, dropna=True):
    """Convert time series data to supervised data for RNN

    Params:
    df: pd.DataFrame
    lag: lags as features
    dropna: default True

    Return:
    ret: pd.DataFrame, with column-names of xxx(t-1)
    """
    cols, col_names = [], []

    # shift `df` to get lags dataframe
    for lag in range(lag, 0, -1):
        cols.append(df.shift(lag))
        col_names.extend(["{0}(t-{1})".format(i, lag) for i in df.columns])

    # append original dataframe
    cols.append(df)
    col_names.extend(df.columns)

    # concate list(df) to get supervised dataframe
    ret = pd.concat(cols, axis=1)
    ret.columns = col_names

    # drop rows containing nan
    if dropna:
        return ret.dropna()
    else:
        return ret

#%%
def history_plot(history):
    """Plot model history

    Params:
    history: return of model.fit

    Return:
    None
    """

    # plt setting
    plt.figure(figsize=(12, 10))
    plt.subplots_adjust(
        bottom=0,
        left=0.01,
        right=0.99,
        top=0.99,
        hspace=0.55
    )

    trends = [i for i in history.history.keys()
        if i[:4] != "val_"]
    ncols = 2
    nrows = (len(trends) + 1) // 2

    for i, t in enumerate(trends):
        plt.subplot(nrows, ncols, i+1)
        plt.title(t.upper())
        plt.plot(history.history[t])
        plt.plot(history.history["val_"+t])
        plt.legend(["train", "validation"])
    plt.show()
#%%
