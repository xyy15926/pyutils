#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: __init__.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:55:16
#   Updated at: 2020-09-07 18:55:19
#   Description: top `__init__.py` contains all kinds of
#     settings for the whole package
#----------------------------------------------------------

# set up logger
# then the modules in the package could get logger with
# `logging.getLogger()`
from .utils import logger
logger.setup_logging("logging.yml")

# set up type remark
from typing import (Any, NoReturn)
from typing import (Tuple, Union, Optional)
from typing import (NewType, TypeVar, Generic)
from typing import (List, Dict)
from collections.abc import (Callable, Sequence, Mapping)
Vector = List[Union[int, float]]
T = TypeVar('T')
class GenericClass(Generic[T]):
    pass

import os
ROOT_PATH = os.path.dirname(__file__)
