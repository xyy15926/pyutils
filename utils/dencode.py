# %%
import base64
from typing import (Any, Union, Tuple)

#%%
def decode_b64(
   s: Union[str, bytes],
   padding:str = "="
) -> bytes:
    """
    Description:
    1. Decode `s` encoded with base64 which may be stripped
       of `=`

    Params:
    s:
    padding: "=" as default

    Return:
    bytes
    """
    # Pad `s` if padding is stripped
    missing_padding = len(s) % 4
    if missing_padding != 0:
        s += padding * (4 - missing_padding)
    # Encode `s` with ASCII if `s` is string
    if isinstance(s, str):
        s = s.encode("ASCII")

    return base64.decodebytes(s)

# %%
