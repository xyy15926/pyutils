#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: converter.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:56:01
#   Updated at: 2020-09-07 18:56:02
#   Description:
#----------------------------------------------------------
#%%
import pandas as pd 
import numpy as np
import logging
logger = logging.getLogger("xutils.converter")
import .dtool
import .calculator
import .dtype

#%%
def convert_series_dtype(dt):
    """
    Description:
    Convert series' dtype automatically according to dt's 
    first elements

    Params:
    dt: series

    Return:
    dt: series with proper dtype
    dtype: str, class or "other"(when no proper dtype found)
    """
    _first = dt[dt.first_valid_index()]

    # dtype == str: try to find proper dtype
    if isinstance(_first, str):
        _first_converted = utils.convert_type(_first)
        # convert data type sucessfully
        # try to convert the whole series
        if not isinstance(_first_converted, str):
            try:
                dt = dt.astype(utils.pdtyper(_first_converted))
                logger.info("`%s` is converted to %s properly",
                        dt.name, type(_first_converted))
                return dt, type(_first_converted)
            except ValueError as ex:
                logger.warning("%s can't be converted to %s: %s",
                        dt.name or _first, type(_first_converted), ex)
        else:
            logger.info("`%s` can't be converted to other dtype properly",
                    dt.name)
            return dt, str

    # elif dtype == object: some values must be converted to target
    # dtype manually
    elif dt.dtype == object:

        # find and convert the values that need to be converted manually
        dt = dt.map(lambda x: utils.convert_type(x, tgt=type(_first)) \
            if isinstance(x, str) else x)

        # try to convert the whole series' dtype
        try:
            dt = dt.astype(type(_first))
            logger.info("`%s` is converted to %s properly",
                    dt.name, type(_first))
            return dt, type(_first)
        except ValueError as ex:
            logger.warning("%s can't be converted to %s: %s",
                    dt.name or _first, type(_first), ex)

    logger.info("`%s` can't be converted to other dtype properly",
            dt.name)
    return dt, type(_first)


# X = pd.DataFrame({"X": ["2020/12/23", "4243"]}, dtype="O")
# # X.X.astype("datetime64")
# print(convert_series_dtype(X.X))

# %%
def categorize_feature(dt, tgt, max_categories=20, predef=[], *,
    spliter=None):
    """
    Description:
    cateogrize feature automatically.

    For features that could be categoriezed:
    1. Numeric feature will be cut into categories
    2. `NaN` will be replaced by "nan"

    For features that can't be categorized:
    Nothing will be done, but return the original series

    Params:
    dt: series
    tgt: target
    max_categories: the maximum of the number of categories,
        except pre-defined categories
    predef: categories which is pre-defined
    spliter: function to split `dt` into stops.
        Decision Tree will be used as default spliter if no 
        `spliter` is passed.

    return:
    woes/dt.name: woes DF, if exists, or series's name will
        be returned
    dt: category series, if exists, or the original series
        will be returned
    """

    dt, _type = convert_series_dtype(dt)
    _value_count = dt.value_counts()

    # describer being an integer means that there is too
    # many categories here, try to convert `dt` to other dtype
    if len(_value_count) > max_categories:
        # `datetime64`/`string` can't be converted into proper
        # dtype, or namely can't be categorized
        if _type in utils.TYPE_ORDERED:
            # use Descision Tree as default spliter for ordered
            # `NaN` will be filled with "nan" here
            spliter = spliter or dtool.tree_spliter
            categorized_dt, categories = spliter(dt, tgt, max_categories, predef)

            woes, monotonic = calculator.get_woe_iv(categorized_dt, tgt)
            # warn if woes is not monotonic
            if not monotonic:
                logger.warning("`%s`'s woe values isn't monotonic", dt.name)

            return woes, categorized_dt
        # so `None` will be returned
        else:
            logger.info("`%s`'s with dtype-%s can't be categorized", dt.name, _type)
            return None, None
    else:
        # Attention:
        # 1. fill `NaN` with "nan" explicitly here
        # 2. convert dtype to `category` or `TypeError` will
        #   be raised if elements in `dt` arn't comparable
        #   for they will be set as index after `groupby`
        dt = dt.fillna("nan").astype("category")
        woes, _ = calculator.get_woe_iv(dt, tgt)
        return woes, dt

