#!  /usr/bin/python3
#----------------------------------------------------------
#   Name: data_cleaning.py
#   Author: xyy15926
#   Created at: 2018-09-14 10:24:37
#   Updated at: 2018-10-11 11:30:27
#   Description: 
#----------------------------------------------------------

import pandas as pd
import numpy as np
from common.fstr import strip_str, rid_invalid
from common.ffunctools import FuncsChain

class DataCleaner:

    def __init__(df, *, skip_cols=None)
        '''DataFramecleaner
        :param df: DataFrame need to be processed
        :param skip_cols: columns remain intact when add
            functions to all handlers
        '''

        self.df = df
        self.valid_cols = [col for col in df.columns if col not in skip_cols]
        self.handlers = dict()

    def _append_func(self, func, args, kwargs, col):
        '''add functions to handler
        :param col: columns in df
        :param func: functions that will be append to col-handler
        :param args: args for func
        :param kwargs: kwargs for func
        '''

        if self.hanlders.get(col):
            self.handlers[cols].append(func, args, kwargs)
        else:
            self.handlers[cols] = FuncsChain()
            self.handelrs[cols].append(func, args, kwargs)

    def add_handler_func(self, func, args, kwargs, *, cols=None):
        '''add functions to handler
        @_append_func
        '''

        if not cols:
            # if no column is specified, `func` will be append to
            # all handlers by default
            for col in self.valid_cols:
                self._append(func, args, kwargs, col)
        else:
            if cols in self.df.columns:
                # if `cols` already exists `self.df`, append `func`
                # to the col-handler only
                self._append(func, args, kwargs, cols)
            else:
                # if `cols` doesn't exist in `self.df`, try to iterate
                for col in cols:
                    if col not in self.df.columns:
                        raise KeyError("column: {!s} not exists".format(col))
                    self._append(func, args, kwargs, col)

    def apply_handlers(self, once=False):
        '''apply handlers on related columns
        :param once: whether clean handler after applied
        '''

        for col, handler in self.hanlders.items():
            self.df[col].apply(handler)
            if once:
                handler.clean()

    def set_strip(self, patterns):
        '''add `strip_str to handlers
        :param patterns: determine what kinds of chars should
            be striped with
            -   list: this will be applied to all columns
            -   dict: applied according to key-value projecting
                relations
        '''

        if isinstance(patterns, dict):
            for col, sps in patterns:
                self.add_handler_func(strip_str, (sps), cols=col)
        else:
            self.add_handler_func(strip_str, (patterns))

    def set_invalid(self, patterns):
        '''add `rid_invalid` for handlers
        :param null_patterns: determine what kind of value will
            be regarded as null, namely invalid value
            -   list: this will be applied to all columns
            -   dict: applied according to key-value projecting
                relations
        '''

        if isinstance(patterns, dict):
            for col, sps in patterns:
                self.add_handler_func(rid_invalid, (sps), cols=col)
        else:
            self.add_handler_func(rid_invalid, (patterns))


    def set_en_symbols(self, cols):
        '''add `to_en_symbols` for handlers
        :param cols: columns that `to_en_symbols` will be added
        '''
        self.add(to_en_symbols, cols=cols)

    def set_lower(self, cols):
        '''add `to_lower` to handlers
        :param cols: columns that `to_lower` will be added
        '''
        self.add_handler_func(to_lower, cols)

    def combine_columns(self, cols, new_col_name):
        '''combine columns provide similiar infomation
        :param cols: columns provide similiar infomation
        :param new_col_name: name assigned to the new column
        '''

        if new_col_name in self.df.columns:
            raise KeyError("column: {!s} exists".format(new_col_name))

        _tmp = self.df[cols[0]]
        for col in cols[1:]:
            _tmp = _tmp.combine_first(self.df[col])
        self.df[new_col_name] = _tmp


    def drop_dup(self, primary):
        '''conbine infomatiom within group, then keep only one
            records
        :param primary: col(s) to groupby
        note: `df.drop_duplicated` may be faster if combining
            infomation if not necessary
        '''

        _groups = self.df.groupby(primary)
        for key, indexs in _groups.groups.items():
            if len(indexs) > 1:
                self.df.ix[indexs].fillna(method="bfill")
                self.df = self.drop(indexs[1:])

def clean_data(df):

    str_strip_patterns = ["spaces", "lower", "upper",
        "digits", "en_symbols", "zh_symbols"]
    num_strip_patterns = ["spaces", "lower", "upper",
        "em_symbols", "zh_symbols"]
    units_strip_patterns = ["spaces"]
    strip_patterns = {
        "spdata_0": str_strip_patterns,
        "spdata_2": str_strip_patterns,
        "test_value": num_strip_patterns,
        "spdata_1": num_strip_patterns,
     #   "spdata_18": units_strip_patterns,
     #   "spdata_16": units_strip_patterns,
     #   "spdata_14": units_strip_patterns,
     #   "spdata_12": units_strip_patterns,
     #   "spdata_10": units_strip_patterns,
     #   "spdata_8": units_strip_patterns,
     #   "spdata_6": units_strip_patterns,
    }

    data_cleaner = DataCleaner(df)
    data_cleaner.set_strip(strip_pattern)
    data_cleaner.set_en_symbols(["units"])
    data_cleaner.add_handler_func("value", lambda s: s.lower())

