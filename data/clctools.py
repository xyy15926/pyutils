# %%
from __future__ import annotations
from collections.abc import (Container, Iterator, Iterable, Sized)
from typing import (Any, Union, Tuple, )
from itertools import (filterfalse, )
MINPAD = 1e-13

# %%
def flatten_iterable(iter_:Iterable) -> Iterable:
    """
    Description:
    Flatten iterable recursively

    WARNING: NO SELF-REFERRENCE ALLOWED

    Params:
    iter_: iterable to be flatten
    flat: iterable to store elements

    Return:
    flat
    """
    flat = []
    for ele in iter_:
        if not issubclass(type(ele), Iterable):
            flat.append(ele)
        else:
            flat.extend(flatten_iterable(ele))
    return flat

def separate_container(iter_: Iterable) -> tuple:
    """
    Description:
    Seperate containers and no-containers in `iter_`

    Params:
    iter_

    Return:
    containers, no-containers
    """
    containers = list(filter(lambda ele: issubclass(type(ele), Container), iter_))
    no_containers = list(filterfalse(lambda ele: issubclass(type(ele), Container), iter_))
    return containers, no_containers


# %%
