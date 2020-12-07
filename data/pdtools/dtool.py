#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: dtool.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:56:10
#   Updated at: 2020-09-07 18:56:12
#   Description:
#----------------------------------------------------------
#%%
import re
import logging
import pandas as pd 
import numpy as np 
from sklearn.tree import DecisionTreeClassifier as DTC
from sklearn.tree import export as export
from sklearn import datasets as sklds
from . import dtyper

#%%
logger = logging.getLogger("xutils.dtool")
LAPLACE_SMOOTH = 0.1

# %%
def flatten_index(dt):
    """
    Description:
    flatten index

    Params:
    dt: dataframe
    """
    logger.debug("flaten `%s`'s MuiltiIndex", dt.name)

    _levels = dt.columns.levels
    _labels = dt.columns.labels
    _new_index = [0] * len(dt.columns)
    _level_n = len(_levels)

    # 1. join columns' names according to the `_levels`、`_labels`
    # 2. eliminate columns with no name
    for zzip in zip(*_labels):
        zzip = list(zzip)
        _new_col_name = "_".join([
            _levels[idx][item] for idx, item in zip(range(_level_n), zzip)
                if not str(_levels[idx][item]).startswith("Unnamed: ")
        ])
        _new_index[zzip[-1]] = _new_col_name

    return _new_index


#%%
#########################################################
# skl.tree._tree.Tree
# 1. children_left: list in which the element is the nodes'
#    left-children's index, -1 if no left-children. So the
#    length must be the number of nodes, namely `capacity`
# 2. children_right: list in which the element is the nodes'
#    right-children's index, -1 if no left-children
# 3. features: list in which the element is the index of
#    the feature for splitting the samples
# 4. threshold: list in which the element is the threshold
#    determines where to split the samples
#########################################################

def tree_spliter(dt, tgt, max_bins=5, predef=[], *,
        clf=None, min_samples_leaf=0.2):
    """
    Description:
    Use descision to split bins

    Params:
    dt: feature series
    tgt: target series
    max_bins: maximum categories
    predef: pre-defined categories, which should be excluded
    clf: tree classifier, de
    min_samples_leaf: minimum ratios of samples for leaf nodes

    Returns:
    cut_dt: dt of bins
    categories: categories
    """

    # this may cause error for `dt`, `tgt` share different indexes
    # dt, tgt = pd.Series(dt).astype(float), pd.Series(tgt).astype(int)
    # valid_dt_bools = dt.notnull() & ~dt.isin(predef)
    # valid_dt = dt[valid_dt_bools].values.reshape(-1, 1)
    # valid_tgt = tgt[valid_dt_bools]

    df = pd.DataFrame({"dt": dt, "tgt": tgt})
    valid_dt_bools = df["dt"].notnull() & ~df["dt"].isin(predef)
    valid_dt = df["dt"][valid_dt_bools].values.reshape(-1, 1)
    valid_tgt = df["tgt"][valid_dt_bools]

    # use tree classifier passed if possible
    # rectify `min_samples_leaf` with valid ratio
    clf = clf or DTC(criterion="entropy",
            splitter="best",
            min_samples_leaf=min_samples_leaf * (valid_dt_bool.sum() / df.shape[0]),
            max_leaf_nodes=max_bins,
            class_weight="balanced",
            min_impurity_decrease=0.1,
            min_weight_fraction_leaf=0.0)
    clf.fit(valid_dt, valid_tgt)

    # get the stops
    stops = sorted(clf.tree_.threshold[clf.tree_.children_left != clf.tree_.children_right])
    stops = np.array([valid_dt.min(), *stops, valid_dt.max()])
    logger.debug("get `%s`'s stops, %s, with decision tree", dt.name, stops)

    # cut `dt` according to the stops
    # Attention: `predef` shoudln't be in any interval defined
        # by `stops`, or `predef` may be cut into some group
    cut_dt = pd.cut(dt, stops, include_lowest=True) \
        .cat.add_categories(["nan", *predef])
    cut_dt[~valid_dt_bools] = dt[~valid_dt_bools].fillna("nan")

    return cut_dt, cut_dt.cat.categories.to_list()


# _wine = sklds.load_wine()
# clf = DTC(criterion="entropy",
#         splitter="random",
#         min_samples_leaf=0.001,
#         max_leaf_nodes=5,
#         class_weight="balanced",
#         min_impurity_decrease=0.1,
#         min_weight_fraction_leaf=0.0,
#         random_state=777777)
# tree_spliter(
#     pd.Series(_wine.data[:, 1]),
#     pd.Series(_wine.target),
#     predef=[5.04, 5.19, 5.51, 5.65, 5.8], clf=clf)


#%%
def chimerge_spliter():
    pass

#%%
def merge_ordered_greedy(t_ratios, queue, min_ratio):
    """
    Description:
    merged comparable items in ascendingly sorted `queue`
    1. try to merge continuous items with ratio < `min_ratio`
        together
    2. if ths ratios' sum of continuous items is still samller
        than `min_ratio`, merged them to next item

    Params:
    t_ratios: series recording the ratio of each item
    queue: sorted deque of comparable items
    min_ratio: low bound of ratios

    Return:
    merged queue
    """
    tmp_merged = None
    new_queue = clct.deque()
    while queue:
        # reset list of temporary merged items
        if not tmp_merged:
            tmp_merged = [queue.popleft(), ]
            tmp_merged_ratio = dtyper.pdidx(t_ratios, tmp_merged[0])
        # pop next item
        if queue:
            _cur = queue.popleft()
        else:
            break

        # if current item's ratio is smaller than lower bound
        # append current item to list of temporary merged items
        _cur_ratio = dtyper.pdidx(t_ratios, _cur)
        if _cur_ratio < min_ratio:
            logger.info("merge `%s`(%f) to `%s`",
                _cur, _cur_ratio, tmp_merged)
            tmp_merged.append(_cur)
            tmp_merged_ratio += _cur_ratio
        else:
            # if merged items' ratios' sum is still too small
            # append current item to list of temporary merged items
            # and then concatenate then list
            if tmp_merged_ratio < min_ratio:
                logger.info("merge `%s`(%f) to `%s`",
                    _cur, dtyper.pdidx(t_ratios, _cur), tmp_merged)
                tmp_merged.append(_cur)
                _merged = concat_ordered(tmp_merged)
                tmp_merged = None
            # concatenate the list directly
            else:
                _merged = concat_ordered(tmp_merged)
                tmp_merged = [_cur, ]

            # append new item to queue of items
            new_queue.append(_merged)

    # handle the remained temporary merged items
    if tmp_merged:
        if tmp_merged_ratio < min_ratio and new_queue:
            logger.info("merge `%s`(%f) to `%s`",
                tmp_merged, tmp_merged_ratio, new_queue[-1])
            new_queue[-1] = concat_ordered([new_queue[-1], *tmp_merged])
        else:
            new_queue.append(concat_ordered(tmp_merged))

    return new_queue

#%%
def merge_ordered(t_ratios, queue, min_ratio):
    """
    Description:
    merged comparable items in `queue` ascendingly sorted
    1. stop merge next items as long as the merged's ratio
        larger than `min_ratio`

    Params:
    t_ratios: series recording the ratio of each item
    queue: queue of items
    min_ratio: low bound of ratios

    Return:
    merged queue of items
    """
    tmp_merged, tmp_merged_ratio = [], 0
    new_queue = clct.deque()
    while queue:
        # pop next items
        cur_item = queue.popleft()
        tmp_merged.append(cur_item)
        tmp_merged_ratio += dtyper.pdidx(t_ratios, cur_item)
        if len(tmp_merged) > 1:
            logger.info("merge `%s`(%f) to `%s`",
                cur_item, dtyper.pdidx(t_ratios, cur_item),
                tmp_merged[:-1])

        # stop merge next item, and append to new queue
        if tmp_merged_ratio >= min_ratio:
            new_queue.append(concat_ordered(tmp_merged))
            tmp_merged, tmp_merged_ratio = [], 0

    # handle the remained temporary merged items
    else:
        if tmp_merged and new_queue:
            new_queue[-1] = concat_ordered([new_queue[-1], *tmp_merged])
        elif tmp_merged:
            new_queue.append(concat_ordered(tmp_merged))

    return new_queue

# %%
def dict2df(
    dt
) -> pd.DataFrame:
    pass

def df2dict(
    dt
) -> pd.DataFrame:
    pass