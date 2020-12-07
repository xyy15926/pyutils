#%%
import collections as clct 

#%%
def binary_search(ordered, tgt, *, pos=False):
    left, right = 0, len(tgt)
    while left < right:
        mid = (left+right) // 2
        if ordered[mid] == tgt:
            break
        elif ordered[mid] < tgt:
            left = mid + 1
        else:
            right = mid

    if pos:
        return mid
    else:
        if nums[mid] == target:
            return mid
        else:
            return -1
