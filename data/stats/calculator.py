#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: calculator.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:56:01
#   Updated at: 2020-09-07 18:56:02
#   Description:
#----------------------------------------------------------
#%%
import os
import logging
import numpy as np
import pandas as pd
import sklearn.metrics as sklm

#%%
logger = logging.getLogger("xutils.calculator")
LAPLACE_SMOOTH = 0.1

# %%
def calculate_woe_iv(cats, Y):
    """
    Description:
    Calculate woe and iv for with the given `cats`, `Y` 
 
    Params:
    cats: categories
    Y: label

    Return:
    df[woe, iv, bad_rate]
    """
    logger.debug("calculate woe and iv values with categories and target")

    df = pd.DataFrame({"Y": Y, "cats": cats})
    df_group = df.groupby("cats")
    # `fillna` to avoid category that not exists in `cats`
    # especially the categories pre-defined
    df_woes = df_group["Y"].agg([
        ("g", lambda y: (y==0).sum()),
        ("b", lambda y: (y==1).sum()),
        ("t", "count")
    ]).fillna(0)

    # handle inf and 0 with laplace smoothing
    df_woes[(df_woes == 0).any(axis=1)] += LAPLACE_SMOOTH

    # cal woe and iv
    df_woes["g_pct"] = df_woes["g"] / df_woes["g"].sum()
    df_woes["b_pct"] = df_woes["b"] / df_woes["b"].sum()
    df_woes["t_pct"] = df_woes["t"] / df_woes["t"].sum()
    df_woes["woe"] = np.log(df_woes["b_pct"] / df_woes["g_pct"])
    df_woes["iv"] = (df_woes["b_pct"] - df_woes["g_pct"]) * df_woes["woe"]

    # check monotonicty of woe
    try:
        _mono = (df_woes.sort_values("woe")["woe"].values == \
                df_woes.sort_index()["woe"].values).all()
    except TypeError as e:
        logger.warning("while checking monotonicty: %s", e)
        _mono = False

    # cal bad rate
    df_woes["b_rate"] = df_woes["b"] / df_woes["t"]

    return df_woes, _mono

# bins = [1, 2, 3, 4]
# X = pd.Series([1, 3, 4, float("nan"), 2, 3, 3])
# Y = pd.Series([0, 0, 0, 0, 1, 1, 1])
# woes = get_woe_iv(pd.cut(X, bins, include_lowest=True), Y)

#%%
def calculate_fpr_tpr(score, tgt):
    pass


#%%

def calculate_auc_ks(tgt, score):
    """
    Description:
    1. Calculate auc, ks
    2. Draw roc curve and ks
    
    Params:
    score: predictions
    tgt: real values

    Return:
    auc
    ks
    """
    # get fpr, tpr, auc, ks
    fpr, tpr, thd = sklm.roc_curve(tgt, score)
    auc = sklm.auc(fpr, tpr)
    ks = (tpr - fpr).max()

    return auc, ks

#%%
def calculate_stats_iteratively(tgt, score, ascending=False):
    """
    Description:
    calculate all the stats of the results
    1. cummulative goods, bads, total
    2. cummulative bads ratio
    3. cummulative total ratio, A.K.A. pass ratio

    Params:
    tgt: label, 1 for bad, 0 for good
    score: 
    ascending: sort score ascendingly or descendingly

    Return:
    dataframe of cummulative stats
    """

    # get cummulative amounts of bads, goods in the order of
    # the predicted scores
    df_cum = pd.DataFrame({"score": score, "tgt": tgt}) \
        .sort_values("score", ascending=ascending) \
        .set_index("score")
    df_cum["cum_t_cnt"] = np.arange(1, len(tgt)+1)

    # traverse to count the number of goods and bads
    # `b_counts[0]` is set just for convenience
    b_cnt = np.zeros(len(tgt)+1)

    # `b_istops` records the indexes of bads for drawing
    # cummulative bads ratio, or bads ratio will falling
    # between stops
    # `predef_stops` records the indexes of stop
    b_istops = []
    for row_idx in range(len(tgt)):
        # fill `b_istops`
        if df_cum["tgt"].iloc[row_idx] == 0:
            b_cnt[row_idx + 1] = b_cnt[row_idx]
        else:
            b_cnt[row_idx + 1] = b_cnt[row_idx] + 1
            b_istops.append(row_idx)
    df_cum["cum_b_cnt"] = b_cnt[1:]

    # select cummulative bad ratios according to `b_istops`
    df_selected = df_cum.iloc[b_istops]
    df_selected["cum_b_ratio"] = df_selected["cum_b_cnt"] / df_selected["cum_t_cnt"]

    return df_selected

# df_iter = calculate_iterative_stats(tgt, score)

#%%
def calculate_stats_intervally(tgt, score, stops):
    """
    Description:

    Params:

    Return:

    """
    # get cummulative amounts of bads, goods in the order of
    # the predicted scores
    df_cum = pd.DataFrame({"score": score, "tgt": tgt})
    df_cum["interval"] = pd.cut(df_cum["score"], stops, include_lowest=True)
    _group = df_cum.groupby("interval")
    df_grouped = _group["tgt"].agg(
        [("g_cnt", lambda tgt: (tgt == 0).sum()),
        ("b_cnt", lambda tgt: (tgt == 1).sum()),
        ("t_cnt", "count")]
    )

    # calculate cummulative statistics
    for col_name in ["g_cnt", "b_cnt", "t_cnt"]:
        _cum_cnt = [0] * (len(stops) - 1)
        _cum_cnt[0] = df_grouped[col_name].iloc[0]
        for iidx in range(1, len(stops) - 1):
            _cum_cnt[iidx] = _cum_cnt[iidx-1] + df_grouped[col_name].iloc[iidx]
        df_grouped["cum_" + col_name] = _cum_cnt
    df_grouped["cum_b_ratio"] = df_grouped["cum_b_cnt"] / df_grouped["cum_t_cnt"]
    df_grouped["cum_g_ratio"] = df_grouped["cum_g_cnt"] / df_grouped["cum_t_cnt"]

    return df_grouped

# df_grouped = calculate_interval_stats(tgt, score, stops)

#%%
if __name__ == "__main__":
    tgt = np.array([0]*10 + [1]*10)
    tgt[15] = 0
    score = np.linspace(0, 1, 20)
    stops = np.linspace(0, 1, 4)
    fpr, tpr, thd = sklm.roc_curve(tgt, score)

# %%
