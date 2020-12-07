#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: string.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:58:38
#   Updated at: 2020-09-07 18:58:41
#   Description:
#----------------------------------------------------------

#%%
import re
import random
import string
from . import (Any, Union, Tuple, ROOT_PATH)

# %%
FTYPE_LOOKUP = {
    # For char
    r"%c": ["(.)", str],
    r"%(\d+)c": [r"(.{1,\1})", str],
    # For integer
    # r"(%0?([1-9]\d*)d)": [r"([-+]?[ \\d]{\2})", int],
    r"%d": [r"([-+]?\d+)", int],
    # For unsigned
    r"%u": [r"(\d+)", int],
    # For hex
    r"%[xX]": [r"([-+]?(?:0[xX])?[\dA-Fa-f]+)", lambda x:int(x,16)],
    # For oct
    r"%o": [r"([-+]?[0-7]+)", lambda x:int(x,8)],
    # For all-integer
    r"%i": [r"([-+]?(?:0[xX][\dA-Fa-f]+|0[0-7]*|\d+))", int],
    # For float
    r"%[eEfg]": [r"([-+]?(?:\d+(.\d*)?|.\d+)([eE][-+]?\d+)?)", float],
    # For string
    r"%s": [r"(\S+)", str]
}
# Re-escape `\` for `re.sub`
RE_FTYPE_LOOKUP = {
    k: re.sub(r"\\([a-zA-z])", r"\\\\\1", v[0]) for k,v in FTYPE_LOOKUP.items()
}
# No-repeat modifier: <modifier>: <key-in-FTYPE_LOOKUP>
# Repeat modifier: <modifier>: (<key-in-FTYPE_LOOKUP>, re-pattern)
MODIFIER_FTYPE_LOOKUP = {
    "c": "%c",
    "Dc": ("%(\d+)c", r"(.{{1,{}}})"),
    "d": "%d",
    "u": "%u",
    "x": "%[xX]",
    "X": "%[xX]",
    "o": "%o",
    "i": "%i",
    "e": "%[eEfg]",
    "E": "%[eEfg]",
    "f": "%[eEfg]",
    "g": "%[eEfg]",
    "s": "%s"
}

# %%
def rescanf(
    fmt:str,
    s:str
) -> tuple:
    """
    Description:
    Something that works just like `fscanf` in C/CPP, but no type
    conversion will applied.

    Params:
    fmt: c-style format string
    s: input string

    Return:
    tuple of string, A.K.A. no dtype convertion applied
    """
    for k, v in RE_FTYPE_LOOKUP.items():
        fmt = re.sub(k, v, fmt)
    return re.match(fmt, s).groups()

def fmt2ptn(
    fmt:str
) -> Tuple[list, list]:
    """
    Description:
    Something that works just like `fscanf` in C/CPP
    1. Type conversion
    2. Less format support

    Params:
    fmt: c-style format string

    Return:
    res: list of regex interpreated from modifiers in fmt
    hanlders: list of callable for parenthesized subgroups
    """
    # Split `fmt` with `%` to get each modifier
    eles = fmt.split("%")
    res, handlers = [], []
    for ele in eles:
        # `fmt` may starts with `%` => check `ele` first
        if not ele:
            continue
        # %<rep><modifier> => append regex and handler directly
        elif ele[0] not in string.digits:
            modifier = ele[0]
            remained_ele = ele[1:]
            # Check if valid modifier
            dtyper = MODIFIER_FTYPE_LOOKUP.get(modifier)
            if dtyper:
                match = FTYPE_LOOKUP[dtyper]
                res.append(match[0] + remained_ele)
                handlers.append(match[1])
        # %<rep><modifier> => get and strip repeats first
        else:
            repeat = re.match("\d+", ele).group()
            ele = ele[len(repeat):]
            modifier = ele[0]
            remained_ele = ele[1:]
            # Check if valid modifier
            _dtyper = MODIFIER_FTYPE_LOOKUP.get(f"D{modifier}")
            if _dtyper: 
                dtyper, ptn = _dtyper
                res.append(ptn.format(repeat) + remained_ele)
                handlers.append(FTYPE_LOOKUP[dtyper][1])
    return res, handlers


def fscanf(
    fmt:str,
    s:str
) -> tuple:
    res, handlers = fmt2ptn(fmt)
    ptn = "".join(res)
    matched = re.match(ptn, s)
    rets = [handler(subg) for handler, subg in zip(handlers, matched.groups())]
    return rets

# fmt = "%s%3c\n%5c %d %d %X"
# s = "2222\naa as 1002332 2302 0x324"
# fscanf(fmt, s)
# rescanf(fmt, s)

# %%
def augmented_strip(
    s:str,
    ptn:str = string.whitespace
) -> str:
    """
    Description:
    1. Augmented

    Params:
    s:
    ptn:

    Return:
    """
    return s.strip(ptn)

# %%
def augmented_replace(
    s:str,
    ptn:str,
    tgt:str,
    part:bool = False
) -> str:
    """
    Description:
    1. Replace `ptn` in `s` with `tgt`

    Params:
    s: original string
    ptn: regex pattern
    tgt: replace target
    part: if part 

    Return:
    """
    if part:
        return re.sub(ptn, tgt, s)
    else:
        if re.search(ptn, s):
            return tgt


# %%
def float_converter(
    s: str
) -> float:
    """
    Description:

    Params:

    Return:

    """
    # Handle "%"
    s = s.strip()

    # Handle ","
    return float(s)




