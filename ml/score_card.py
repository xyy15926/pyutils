#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: score_card.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:55:30
#   Updated at: 2020-09-07 18:55:33
#   Description:
#----------------------------------------------------------
#%%
import pandas as pd 
import numpy as np 
import sys
import datetime
import collections as clct
import matplotlib.pyplot as plt
import statsmodels.api as sm
import itertools as itl
import logging
from ..functions import string as xstr
from ..data_process import dtyper as xtyper

#%%
RANDOM_SEED=7777777
logger = logging.getLogger("main.auto")

#%%
def merge_bins(woe, t_ratios, min_ratio=0.05, keep=[]):
    """
    Description:
    1. Seperate ordered with unordered
    2. Sort and merge ordered
    3. Sort unordered according to their woe value, and then
        merge them

    Params:
    woe: series of woe values
    t_ratio: series of ratios
    min_ratios: the lower bound of the ratio 
    keep: bins that shouldn't be merged

    Return:
    merged ordered
    merged unordered
    """

    ordered_bins = []
    unordered_bins = []

    for ele in woe.index:
        if ele in keep:
            continue
        elif type(ele) in utils.TYPE_ORDERED:
            ordered_bins.append(ele)
        else:
            unordered_bins.append(ele)

    # handle deque of comparable bins
    ordered_bins = xtyper.merge_ordered_bins(
        t_ratios,
        clct.deque(sorted(ordered_bins, key=utils.min_key)),
        min_ratio
    )

    # handle deque of category bins
    # merge unordered category according to their woe values,
    # namely merge bins share closest(maybe) woe value together
    _index_ordered_by_woe = list(woe.sort_values().index)
    unordered_bins = xtyper.merge_ordered_bins(
        t_ratios,
        clct.deque(sorted(
            unordered_bins,
            key=lambda x: _index_ordered_by_woe.index(x)
        )),
        min_ratio
    )

    return ordered_bins, unordered_bins


# %%
def select_features_with_iv(iv_sum, max_num=10, max_per=0.3, *,
    iv_min=0.02, iv_max=100):
    """
    Description:
    select features according to iv values

    Params:
    iv_sum: series with iv values
    max_num: maximum number of features
    max_per: maximum percentage of the numbers of the whole features
    iv_min: the lower bound of iv value of valid features
    iv_max: the uppper bound of iv value of valid features

    Return:
    selected features
    """
    _maxf = int(max(max_num, len(iv_sum) * max_per))
    iv_sum_valid = iv_sum[iv_sum >= iv_min][iv_sum < iv_max].sort_values(ascending=False)

    return iv_sum_valid.iloc[:_maxf]


#%%
def select_features_with_correlation(dt, iv, max_coef=0.95):
    """
    Description:
    features with larger iv values will be remained if two
    features' correlation coefficient is closed to 1

    Params:
    dt: dataframe with woe values of samples
    iv_sum: mapper with iv  values of fatures
    max_coef: upper bound of correlation coefficient

    Returns:
    dataframe with remained features
    """
    remained_cols = [1] * len(dt.columns)

    # get indexs of columns which coef is to large
    _coefs = np.abs(np.triu(np.corrcoef(dt.values.T)) - \
            np.eye(len(dt.columns)))
    _coors = list(itl.product(range(_coefs.shape[0]), range(_coefs.shape[1])))
    _coors = np.array(_coors).reshape(*_coefs.shape, -1)

    # remove features with smaller iv values
    # attention: feature may have be removed before
    for row, col in _coors[_coefs > max_coef]:
        if iv[dt.columns[row]] > iv[dt.columns[col]]:
            remained_cols[col] = 0
        else:
            remained_cols[row] = 0

    return dt.columns[pd.Series(remained_cols, dt.columns, dtype=bool)]

# dt = X2[["X2_woe", "X1_woe"]]
# dt.columns = ["X2", "X1"]
# dt = select_features_with_correlation(dt, iv, 0.95)

#%%
def detect_features(dt, tgt, max_bins=20, bins=[],
    dpath="output/"):
    """
    Description:
    handle the whole dataframe

    Params:
    df: dataframe
    tgt: target
    max_bins: the maximum number of bins
    bins: pre-defined categories

    Return:
    rets: dataframe recording woe, iv, etc. this will also
        be store to disk as excel
    dt: dataframe filled with relating category value
    """

    dict_woes = {}
    df_new = pd.DataFrame()
    df_woe = pd.DataFrame()

    # 1. pre-process each feature
    # 2. try to categorized each features
    for ser in dt:
        # preprocess: data-cleaning, etc
        df_new[ser] = dt[ser].map(lambda x: xstr.str_striper(x))
        #TODO

        # try to categorize feature
        _bins = None
        if isinstance(bins, list):
            _bins = bins
        elif isinstance(bins, dict) or isinstance(bins, pd.Series):
            _bins = bins[ser]
        else:
            raise ValueError("list-like or mapper should be passed, instead of {!s}".format(bins))
        _woe, _new = categorize_feature(df_new[ser], tgt, max_bins, _bins) 
 
        # record results
        if not _woe is None:
            dict_woes[ser] = _woe
            df_new[ser] = _new
            df_woe[ser] = df_new[ser].map(_woe["woe"])

    # convert index's dtype to str to `concat` dataframes with
    # imcompatible index, for they can't compare with others
    _for_disk_rets = pd.concat(
        [v.set_index(v.index.astype(str)) for v in dict_woes.values()],
        keys=dict_woes.keys(),
        names=["features", "cats"]
    )
    # try to store `rets` to file
    try:
        _for_disk_rets.to_excel(dpath + "woe_iv.xlsx")
    except FileNotFoundError as ex:
        logger.warning("can't store results to directory `%s`", dpath)

    # `_for_disk_rets` won't be returned, for its index
    # has been converted to `str` which isn't convenient
    return dict_woes, df_new, df_woe


#%%
def merge_categories(woes, df_new, tgt, min_ratio=0.05, *, keep=[]):
    """
    Description:

    Params:

    Return:
    """

    # map elements to category
    def _map2cat(ele, _sets):
        for _set in _sets:
            if dtype.isin(ele, _set):
                return _set
        else:
            logger.warning("`%s` can't be mapped in `%s`", ele, _sets)
            return ele

    df_updated = pd.DataFrame()

    # dict-type `woes` and df-type `woes` share different procedures
    # `.astype("category")` to avoid error in `groupby`, where
    # comparing is needed
    for feature in woes.keys():
        ordered, unordered = merge_bins(
            woes[feature]["woe"], woes[feature]["t_pct"],
            min_ratio, keep=keep
        )
        ordered.extend(unordered)
        ordered.extend(keep)
        df_updated[feature] = df_new[feature].map(
            lambda x: _map2cat(x, ordered)
        ).astype("category") 
        
    woes_updated = {col: utils.get_woe_iv(df_updated[col], tgt)[0] for col in df_updated}
    df_woe_updated = pd.DataFrame({col: df_updated[col].map(woes_updated[col]["woe"]) for col in woes.keys()})

    return woes_updated, df_updated, df_woe_updated


# %%
def recover_params_from_excel(fpath):
    """
    Description:
    Recover dataframe of woe, iv from existing file
    """
    pass


#%%
def build_score_card(params, woes, pdo=20, dpath="output/"):
    """
    Description:
    build score card
    
    Params:
    params: coefficents from LR
    woes: woe values of each features
    pdo: how much scores needed to reduce the odds to half
    dpath: the directory to store results

    Return:
    score_card: woe values and scores
    """
    # calculate `B` according to `pdo`
    B = pdo / np.log(2)
    score_card = {}

    # calculate scores of each features' categories
    for feat, woe in woes.items():
        for cat in woe.index:
            _one_woe = utils.pdidx(woe, cat)
            score_card[(feat, cat)] = [_one_woe, -B * params[feat] * _one_woe]
    score_card = pd.DataFrame(score_card, index=["woe", "scores"]).T
    score_card.index.names = ["features", "categories"]

    # try to store score_card to disk
    try:
        score_card.to_excel(dpath + "score_card.xlsx")
    except FileNotFoundError as ex:
        logger.warning("can't store results to directory `%s`", dpath)

    return score_card

#%%
# def auto_main(dt, tgt):
#     woes, df_new, df_woe = auto_detect_features(dt, tgt)
#     feats_iv = select_features_with_iv(woes["iv"])
#     df_woe = select_features_with_correlation(df_woe[feats_iv.index], feats_iv, 0.95)
#     lr_model, selected_feats, aics, bics = fit_lr_model(sm.add_constant(df_woe), tgt)
#     score = lr_model.predict(sm.add_constant(df_woe)[lr_model.params.index])
#     auc, ks = get_auc_ks(score, tgt)
#     score_card = build_score_card(
#         lr_model.params[selected_feats],
#         woes["woe"][selected_feats])

#     return score_card

if __name__ == "__main__":
    _today = datetime.datetime.strptime("20200707", "%Y%m%d")
    dt = pd.DataFrame(
        {
            "X1": [1] * 20 + [0] * 20,
            "X2": list(range(1, 41)),
            "X3": [chr(i) for i in range(ord('a'), ord('a') + 40)],
            "date": [datetime.date.isoformat(_today.replace(month=i)) for i in range(1, 11)] * 4
        }, dtype="O")
    tgt = pd.Series([1] * 19 + [0] * 20 + [1])
    dt.X1[2] = float("nan")
    dt.X1[34] = float("nan")
    dt.X1[23] = ">5"
    dt.X1[25] = ">5"
    dt.X2[12] = float("nan")
    dt.X2[34] = float("nan")
    dt.X3[36] = float("nan")
    bins=[-999.0]

    woes, df_new, df_woe = detect_features(dt, tgt, 20, bins)
    a, b, c = try_merge_categories(woes, df_new, tgt, 0.3, keep=bins)
    woes, df_new, df_woe = a, b, c
    feats_iv = select_features_with_iv(
        pd.Series({k: v["iv"].sum() for k,v in woes.items()})
    )
    feats_cor = select_features_with_correlation(df_woe[feats_iv.index], feats_iv, 0.95)
    lr_model, selected_feats, aics, bics = fit_lr_model(sm.add_constant(df_woe[feats_cor]), tgt, 1, 1)
    score = lr_model.predict(sm.add_constant(df_woe)[lr_model.params.index])
    auc, ks = get_auc_ks(score.values, tgt.values)
    score_card = build_score_card(
        lr_model.params[selected_feats],
        {k: woes[k]["woe"] for k in selected_feats}
    )

#%%
