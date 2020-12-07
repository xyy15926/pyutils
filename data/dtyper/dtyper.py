#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: dtyper.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:56:18
#   Updated at: 2020-09-07 18:56:21
#   Description:
#----------------------------------------------------------
#%%
from typing import (Union, Any)
import pandas as pd 
import numpy as np 
import re
import logging
#%%
logger = logging.getLogger("xutils.dtype")

#%%
# ONLY HASHABLE DTYPE LISTED HERE
TYPE_REGEX = {
    # `int` regex is really complicated
    # `(?<![\.\d])` will exclude the integer part of float,
    # so `(?![\.])` does fractions
    # `(?<![-/])` will exclude the y.m.d of date
    "int": "(?<![\.\d\-/])[+-]?\d+(?![\.\d\-/])",
    # "float" regex contains "int"
    "float": "[+-]?\d+(?:\.\d*)?",
    # this can handle 02/29
    "datetime64": "(?!0000)[0-9]{4}[-/]((0[1-9]|1[0-2])[-/](0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)",
    # only right-closed interval supported
    "interval": "\([+-]?\d+(?:\.\d*)?, *[+-]?\d+(?:\.\d*)?\]",
    # frozenset is hashable
    "frozenset": "\([+-]?\d+(?:\.\d*)?, *[+-]?\d+(?:\.\d*)?\)",
    "nan": "nan",
}
TYPE_CONVERTER = {
    "int": int,
    "float": float,
    "datetime64": pd.to_datetime,
    "interval": lambda x: pd.Interval(*(map(lambda _x: float(_x.strip()), x.strip()[1:-1].split(",")))),
    "frozenset": lambda x: frozenset(map(lambda _x: float(_x.strip()), x.strip()[1:-1].split(","))),
    "nan": float,
}
TYPE_ENUMS = {
    "int": frozenset([int, np.int8, np.int16, np.int32, np.int64]),
    "float": frozenset([float, np.float16, np.float32, np.float64]),
    "datetime64": frozenset([pd.Timestamp,]),
    "interval": frozenset([pd.Interval,]),
    "frozenset": frozenset([frozenset, set]),
    "nan": frozenset([float,]),
}
TYPE_MIXIN = frozenset([
    *TYPE_ENUMS["interval"],
    *TYPE_ENUMS["frozenset"],
])
TYPE_SINGLE = frozenset([
    *TYPE_ENUMS["int"],
    *TYPE_ENUMS["float"],
    *TYPE_ENUMS["datetime64"],
])
TYPE_ORDERED = frozenset([
    *TYPE_ENUMS["int"],
    *TYPE_ENUMS["float"],
    *TYPE_ENUMS["datetime64"],
    *TYPE_ENUMS["interval"],
    *TYPE_ENUMS["frozenset"],
])

#%%
def min_key(ele: Any) -> Any:
    """
    Description:
    minimum key function for `sort`
    1. interval will be represented by its left edge
       (doesn't consider that the left edge isn't not included)
    2. frozenset will be represented by its minimum elements

    Params:
    ele: ele in array-like to be sorted

    Return:
    element which is comparable
    """
    if type(ele) in TYPE_ENUMS["interval"]:
        return ele.left + 1e-7
    if type(ele) in TYPE_ENUMS["frozenset"]:
        return min(ele)
    return ele

def max_key(ele: Any) -> Any:
    """
    Description:
    Maximum key function for `sort`
    1. interval will be represented by its right edge
    2. frozenset will be represented by its maximum elements

    Params:
    ele: ele in array-like to be sorted

    Return:
    element which is comparable
    """
    if type(ele) in TYPE_ENUMS["interval"]:
        return ele.right
    if type(ele) in TYPE_ENUMS["frozenset"]:
        return max(ele)
    return ele

#%%
def isin(ele: Any, container: Any) -> bool:
    """
    Description:
    Check if `ele` in `container`.
    Remark: `ele == container` will be regarded as `ele in container`

    Params:
    ele: content to be determined
    container: container

    Return:
    bool
    """

    # no-range container: `in` means `==`
    if type(container) in TYPE_SINGLE:
        return ele == container
    # interval container
    elif type(container) in TYPE_ENUMS["interval"]:
        # check if container-range cover ele-range entirely
        if type(ele) in TYPE_ENUMS["interval"]:
            return ele.left >= container.left and ele.right <= container.right
        # `ele` with improper dtype will raise error, just return false
        else:
            try:
                return ele in container
            except:
                return False
    # set container
    else:
        return ele in container

#%%
def pdidx(dt: Union[pd.Series, pd.DataFrame], idxer: Any) -> Any:
    """
    Description:
    1. Pandas regard set, forzenset, etc as list-like indexer,
        so frozenset can't be used to fetch value directly

    Params:
    dt: series or df
    idxer: index to get value

    Return:
    """
    if type(idxer) in TYPE_ENUMS["frozenset"]:
        return dt.iloc[list(dt.index).index(idxer)]
    else:
        return dt.loc[idxer]

#%%
def is_overlapped(seq: list, *, sorted_: bool = False) -> bool:
    """
    Description:
    1. Check if elements in `seq` overlap

    Params:
    seq:
    sorted_: if seq is ordered

    Return:
    """
    if not sorted_:
        seq_ = seq.copy()
        sorted(_seq, key=min_key)
    else:
        seq_ = seq

    for ele_before, ele_later in zip(seq_[:-1], seq[1:]):
        if max_key(ele_before) >= min_key(ele_later):
            return True
    return False

#%%
def intervals_from_list(seq: list, how_left:str="include", how_right:str="exclude") -> list:
    """
    Description:
    1. Contruct intervals from list

    Params:
    seq: list of numbers determines intevals
    how_left: what to do with left_edge of the first interval
    how_right: what to do with right_edge of the last interval

    Return:
    list of intervals
    """
    # construct seqences of the left-edges
    if how_left == "inf":
        left_eles = [float("-inf"), *seq[:-1]]
    elif how_left == "include":
        assert(len(seq) > 1)
        left_eles = [seq[0] - 1e-9, *seq[1:-1]]
    elif how_left == "execlude":
        left_eles = seq[:-1]
    else:
        logger.warning(f"unrecognzed parameters for `how_left`: {how_left}")
        left_eles = seq[:-1]

    # construct seqences of the right-edges
    if how_right == "inf":
        right_eles = [*seq[1:], float("inf")]
    elif how_right == "include":
        assert(len(seq) > 1)
        right_eles = [*seq[1:-1], seq[-1] + 1e-9]
    elif how_right == "execlude":
        right_eles = seq[1:]
    else:
        logger.warning(f"unrecognzed parameters for `how_right`: {how_left}")
        right_eles = seq[1:]

    # construct intervals
    intervals_ = [pd.Interval(l_, r_) for l_, r_ in zip(left_eles, right_eles)]
    return intervals_

#%%
def find_all(seq: Any, target: Any, ordered:bool=False, *, key: Any=None) -> list:
    """
    Description:
    1. find all the elements in seq that contains `target`
    2. if sorted, binary search will be used. Or, travesal will be applyed

    Params:
    seq:
    target:
    ordered:
    key: key function determine how to compare elements in `seq`

    Return:
    list of eles that contains `target`
    """
    key = key or (lambda x: x)
    if not ordered:
        rets = [ele for ele in seq if isin(target, key(ele))]
    else:
        #TODO
        rets = []
        pass 
    return rets


#%%
def concat_ordered(ordered: Any) -> Any:
    """
    Description:
    Concatenate comparable values in `ordered`, which may
    contains integer, float, interval, and datetime64, etc.

    Params:
    ordered: list of comparable values in ascending order

    Return:
    concatenated ordered items
    """
    # ugly flag, wuwuwuwu
    # but it's necessary to check every elements in `ordered`
    _interval_flag = 0
    _tmp_set, _set_flag = None, 0
    for ele in ordered:
        # interval found: interval returned
        if type(ele) in TYPE_ENUMS["interval"]:
            _interval_flag = 1
        # set found: set return
        elif type(ele) in TYPE_ENUMS["frozenset"]:
            _set_flag = 1
            _tmp_set = set(ele)

    if _interval_flag:
        if type(ordered[0]) in TYPE_ENUMS["interval"]:
            _left = min_key(ordered[0])
        # interval doesn't include left-edge, so move left-edge little lefter
        # if the left-edge is determined by int, float or set
        else:
            _left = min_key(ordered[0]) - 1e-7
        return pd.Interval(_left, max_key(ordered[-1]))
    elif _set_flag:
        # frozenset isn't editable, so temporary set is needed
        for _ele in ordered:
            if _ele in TYPE_ENUMS["frozenset"]:
                _tmp_set.update(_ele)
            else:
                _tmp_set.add(_ele)
        return frozenset(_tmp_set)
    # no set nor interval exists, return `frozenset` directly
    else:
        return frozenset(ordered)

#%%
def pdtyper(ele: Any) -> Any:
    """
    Description:
    Just for pandas 1.1.1, where`.astype` doesn't support `pd.Timestamp`
    and no idea why this occurs

    Params:
    ele: object

    Return:
    dtype or string indicating dtype
    """
    if type(ele) in TYPE_ENUMS["datetime64"]:
        return "datetime64"
    else:
        return type(ele)

#%%
def convert_type(ele_str, *, tgt=None) -> Any:
    """
    Description:
    Convert string to proper data type

    Params:
    ele_str: string
    tgt: target dtype

    Return:
    value with proper date type
    """
    assert(isinstance(ele_str, str))

    # if no target dtype is provided, try to convert to
    # proper dtype according to regex
    # these kinds of values with goal data type could be
    # converted to original string properly
    if not tgt:
        for k, v in TYPE_REGEX.items():
            if re.match(v+"$", ele_str):
                return TYPE_CONVERTER[k](ele_str)
        else:
            return ele_str
    # try to convert to target dtype
    # attention: the following type converting is irreversible
    else:
        if tgt == "int" or tgt in TYPE_ENUMS["int"] or \
            tgt == "float" or tgt in TYPE_ENUMS["float"]:

            if tgt == "int" or tgt in TYPE_ENUMS["int"]:
                tgt = "int"
            else:
                tgt = "float"

            # find possible values according to regex
            _ret = re.findall(TYPE_REGEX[tgt], ele_str)

            # convert string with pattern like ">10", "大于10" to
            # pd.Interval(10, inf)
            if "大" in ele_str or ">" in ele_str:
                _tgt_ret = TYPE_CONVERTER[tgt](_ret[0])
                _tgt_interval = pd.Interval(_tgt_ret, float("inf"))
                logger.info("`%s` has been converted to `%s`", ele_str, _tgt_interval)
                return _tgt_interval

            # convert string with pattern like "<10", "小于10" to
            # pd.Interval(-inf, 10)
            elif "小" in ele_str or "<" in ele_str:
                _tgt_ret = TYPE_CONVERTER[tgt](_ret[0])
                _tgt_interval = pd.Interval(-float("inf"), TYPE_CONVERTER[tgt](_ret[0]))
                logger.info("`%s` has been converted to `%s`", ele_str, _tgt_interval)
                return _tgt_interval

            # convert string with pattern like "10-20", "10至20" to
            # pd.Interval(10, 20)
            elif ("-" in ele_str or "至" in ele_str or "间" in ele_str) \
                and len(_ret) == 2:
                _left_ret, _right_ret = map(TYPE_CONVERTER[tgt], _ret)
                _tgt_interval = pd.Interval(_left_ret, _right_ret)
                logger.info("`%s` has been converted to `%s`", ele_str, _tgt_interval)
                return _tgt_interval

            # convert string with `,`, `%`
            #TODO

            # nothing can do but raise error
            else:
                raise ValueError("can't convert `%s` to `%s`" % (ele_str, tgt))

        # other target data type need to be added
        else:
            raise ValueError("can't convert `%s` to `%s`" % (ele_str, tgt))
