##########################################################
#
# 20201201:
# 1. Finish `Interval` and `Value`'s infrastructure
#
# 20201202:
# 1. Implement `__add__`, `__sub__` for `Intervals` and
#    `Value`
# 2. `Value`'s `__add__`, `__sub__` depend much on
#    `Interval`'s, which will be inefficient
#
# 20201203-V1:
# 1. Re-write `Value`'s `__add__`, `__sub__` which doesn't
#    depend on `Interval`'s `__add__`, `__sub__`. But this
#    implementation depends much on inner structure of
#    `Value`, and two implementations from `Interval` and
#    `Value` is annoying
# 
# 20201203-V2:
# 1. Add `cls.intervals_diff_intervals`, 
#    `cls.intervals_diff_sized`, etc to get `Value` rid
#    of the dependence of `Value`'s inner structure
#
# 20201206:
# 1. Re-write most of `Interval`'s static method, as along
#    as `__add__` and `__sub__` of both `Interval` and
#    `Value`
#
#TODO: `Value.__add__`, `__sub__` could be optimized under
#      the condiditon that parameters are no-iterable 
##########################################################
# %%
from __future__ import annotations
import re
from collections.abc import (Container, Iterator, Iterable, Sized, Callable)
from collections import (deque, )
from typing import (Any, Union, Tuple, )
from .clctools import (flatten_iterable, separate_container)
MINPAD = 1e-13

# %%
def max_key(item: Any) -> Any:
    """
    Description:
    1. Key function for function like `sort`, which return the
       maximum in `item`

    Params:
    item

    Return:
    maximum in `item`
    """
    if issubclass(type(item), Interval):
        return item.max()
    else:
        return item

def min_key(item: Any) -> Any:
    """
    Description:
    1. Key function for function like `sort`, which return the
       minimum in `item`

    Params:
    item

    Return:
    minimum in `item`
    """
    if issubclass(type(item), Interval):
        return item.min()
    else:
        return item

# %%
class Interval(Container):
    def __init__(
        self,
        left:Union[int, float]=float("nan"),
        right:Union[int, float]=float("nan"),
        including_left:bool=True,
        including_right:bool=False
    ) -> None:
        """
        Description:
        `Interval` act just like interval in mathematics:
        1. Contain
        2. Include edge
        3. Maximum and minimum
        And it can also:
        1. Compare with other `Interval`, containers, int, etc
        2. Do addition, subtraction, etc with ohter containers, int, etc

        Params:
        left:
        right:
        including_left:
        including_right:

        Return:
        """
        self.including_left = including_left
        self.including_right = including_right
        self.left = left
        self.right = right
        self.__set_edge()

    def __set_edge(self) -> None:
        """
        Description:
        Set "edge" for comparsion:
        1. including-left: `_left` = `left`
        2. not including-let: `_left` = `left` + MINPAD
        """
        self._left = self.left if self.including_left else self.left + MINPAD
        self._right = self.right if self.including_right else self.right - MINPAD

    def __contains__(self, item: Any, closed:bool=False) -> bool:
        """
        Description:
        `__contains__` with parameter `closed`

        Params:
        closed: if including both edges at any time

        Return:
        If `self` contains `item`
        """
        if closed:
            _min, _max = self.left, self.right
        else:
            _min, _max = self.min(), self.max()

        if issubclass(type(item), Iterable):
            return (_min < min(item)) and (max(item) < _max)
        else:
            return _min < item < _max

    def max(self) -> Union[int, float]:
        """
        Description:
        1. Return the maximum, A.K.A. `_right`
        """
        return self.right if self.including_right else self.right - MINPAD

    def min(self) -> Union[int, float]:
        """
        Description:
        1. Return the minimum, A.K.A. `_left`
        """
        return self.left if self.including_left else self.left + MINPAD

    def __lt__(self, other: Any) -> bool:
        """
        Description:
        1. `self < other` only when maximum in self less than other
        """
        return self.max() < other

    def __gt__(self, other: Any) -> bool:
        """
        Description:
        1. `self > other` only when minimum in self larger than other
        """
        return self.min() > other

    def __eq__(self, other: Any) -> bool:
        """
        Descrition:
        1. `self == other` only when both has the same edge, A.K.A
           `self in other and other in self`
        """
        return (self in other) and (other in self)

    def __add__(self, other:Any, mutable:bool=False) -> Any:
        """
        Description:
        1. `other`: int, float, Interval -> `.extend`
        2. `other`: [int, float, Interval] -> `intevervals_union_XXX`

        P.S.
        If self is null, `other` will be returned directly

        Params:
        mutable: whether `self`, `other` could be altered

        Return:
        """
        # If `self` contains no elements, return `other` directly
        if not other:
            return self.copy()

        # If not mutable, copy `self`
        if not mutable:
            self_copy = self.copy()
        else:
            self_copy = self


        # `Other`: not iterable -> call `.extend` directly
        if not issubclass(type(other), Iterable):
            # `Other`: int, float, etc
            if not issubclass(type(other), self.__class__):
                _ret = self_copy.extend(self.__class__.from_single(other))
                if _ret:
                    return Value.from_raw({other, }, [self_copy, ])
                else:
                    return self_copy
            # `Other`: Interval
            else:
                if not mutable:
                    other = other.copy()
                _ret = self_copy.extend(other)
                # Return intervals in only one interval returned,
                #   else return value
                if _ret:
                    return Value.from_raw(set(), sorted([self_copy, other], key=min_key))
                else:
                    return self_copy
        # `Other`: iterable
        # 1. Flatten and separate containers, non-containers in `other`
        # 2. call `intervals_union_intervals`, `intervals_union_sized`
        else:
            other = flatten_iterable(other)
            intervals, sized = separate_container(other)
            # Copy if not mutable
            if not mutable:
                intervals = [itvl.copy() for itvl in intervals]

            intervals = self.__class__.intervals_union_intervals(
                [self_copy, ],
                intervals,
                mutable=True
            )
            sized, intervals = self.__class__.intervals_union_sized(
                intervals,
                sized,
                mutable=True
            )
            # Return interval if only one interval returned,
            #   else return Value
            if (not sized) and (len(intervals) == 1):
                return intervals[0]
            else:
                return Value.from_raw(sized, intervals)

    def __sub__(self, other:Any, mutable:bool=False) -> Any:
        """
        Description:
        1. `other`: int, float, Interval -> `.remove`
        2. `other`: [int, float, Interval] -> `intevervals_diff_XXX`

        P.S.
        If self is null, `NAN_INTERVALS` will be returned directly

        Params:
        mutable: whether `self`, `other` could be altered

        Return:
        """
        # Boundary cases
        # If `self` contains no elements, return null-interval directly
        if not self:
            return NAN_INTERVAL

        # If not mutable, copy `self`
        if not mutable:
            self_copy = self.copy()
        else:
            self_copy = self

        # `Other`: int, float, Interval -> call `.remove` directly
        if not issubclass(type(other), Iterable):
            if issubclass(type(other), self.__class__):
                return self_copy.remove(other)
            else:
                return self_copy.remove(self.__class__.from_single(other))
        # `Other`: [int, float, Interval] -> call `.intervals_diff_XXX`
        else:
            other = flatten_iterable(other)
            intervals, sized = separate_container(other)
            # Copy if not mutable
            if not mutable:
                intervals = [itvl.copy() for itvl in intervals]

            self_copy = self.__class__.intervals_diff_intervals(
                [self_copy, ],
                intervals,
                mutable=True
            )
            self_copy = self.__class__.intervals_diff_sized(
                [self_copy, ],
                sized,
                mutable=True
            )

            # Return interval if only one interval returned,
            #   else return Value
            if len(self_copy) == 1:
                return self.copy[0]
            else:
                return Value.from_raw(set(), self_copy)

    def __repr__(self):
        """
        Description:
        Represent `self` just like interval in mathmathics
        1. `()`, `[]` for open intervals and closed intervals

        Params:

        Return:
        """
        repr_ = ["", ""]
        if self.including_left:
            repr_[0] = f"[{self.left}"
        else:
            repr_[0] = f"({self.left}"
        
        if self.including_right:
            repr_[1] = f"{self.right}]"
        else:
            repr_[1] = f"{self.right})"

        return ",".join(repr_)

    def __bool__(self):
        return self.max() >= self.min()

    @classmethod
    def trim_intervals(cls,
        intervals: Iterable,
        reverse:bool=False,
        mutable:bool=False
    ) -> list:
        """
        Description:
        Trim intervals
        1. Sort `intervals`
        2. Concatenate intervals overlapping with others

        Params:
        intervals
        reverse: whether to reverse the result
        mutable

        Return:
        trimmed intervals
        """
        # Don't just set `reverse` in `sorted`
        # 1. In ascending order -> pop maximum -> sort with `max_key`
        # 2. In descending order -> pop minimum -> sort with `min_key`

        # P.S.
        # If intervals returned by `trim_intervals` overlap with each
        #   other, which means that ordering by left edge and right edge
        #   will leading to different result, `key` should be add as
        #   another parameter.

        # P.S.
        # `Pop` is used here to traverse the whole intervals, while 
        # index increasment could work the same way. But remember to 
        # exchange `key`, `reverse` if using index increasment.
        if reverse:
            itvls = sorted(intervals, key=max_key, reverse=False)
        else:
            itvls = sorted(intervals, key=min_key, reverse=True)

        # Copy each interval if necessary
        if not mutable:
            itvls = [itvl.copy() for itvl in itvls]

        # Merge intervals in turn
        merged = []
        while itvls:
            popout = itvls.pop()
            if merged and merged[-1].overlaps(popout):
                merged[-1].extend(popout)
            else:
                merged.append(popout)

        return merged

    @classmethod
    def merge_intervals(cls,
        left_intervals:Iterable,
        right_intervals:Iterable,
        mutable=False
    ) -> list:
        """
        Description:
        Merge sorted `left_intervals` and `right_intervals` together

        Params:
        left_intervals
        right_intervals
        mutable

        Return:
        merged intervals
        """
        # Check if intervals are null
        if not left_intervals:
            return right_intervals
        if not right_intervals:
            return left_intervals

        # Copy intervals if not mutable
        if not mutable:
            left_intervals = [itvl.copy() for itvl in left_intervals]
            right_intervals = [itvl.copy() for itvl in right_intervals]

        # Merge intervals from `left_intervals` and `right_intervals`
        # in turn
        itvls = []
        lidx, ridx = 0, 0
        while lidx < len(left_intervals) and right < len(right_intervals):
            # P.S.
            # It's better to put `overlap`/`extend` before `<` and `>`
            # For `extend` will check if two intervals adjoines, which
            # will make result more formal.
            # P.S.
            # This should also be applied in functions like add, union, etc.
            # Certainly, functions like subtract, diff, etc could put
            #   if condition as you like.
            if left_intervals[lidx].extend(right_interval[ridx]):
                ridx += 1
            elif left_intervals[lidx] < right_intervals[ridx]:
                itvls.append(left_intervals[lidx])
                lidx += 1
            else:
                itvls.append(right_intervals[ridx])
                ridx += 1

        # Merge rest intervals
        if left_intervals:
            itvls.extend(left_intervals)
        if right_intervals:
            itvls.extend(right_intervals)

        return itvls

    @classmethod
    def intervals_diff_intervals(cls,
        left_intervals:Iterable,
        right_intervals:Iterable,
        trimmed:bool=False,
        mutable:bool=False
    ) -> list:
        """
        Description:
        Calculate the difference of `left_intervals` from `right_intervals`

        Procedure:
        1. Boundary cases
        2. Trim intervals
        3. Calculate the difference by checks intervals from `left_intervals`
           and `right_intervals`

        P.S.
        There are two ways to check intervals in turn
        1. Pop: Pop is good if you don't need to pop many times in the loop.
           But it will be a mass if pop to many times, for you need to
           A. Check the container's emptyness every time before popping
           B. You can't over-pop, which could really help to re-use loop
              boundary checking
        2. Index: Index may not be clear in some way. But over-index really
           helps.

        Params:
        left_intervals: intervals from which to get difference
        right_intervals: intervals with which to subtract
        trimmed: if `left_intervals` and `right_intervals` are trimmed
            1. True: copy each interval directly
            2. False: trim intervals

        Return:
        [Interval]
        """
        # Boundary cases
        if not (left_intervals and right_intervals):
            return left_intervals

        # Sort intervals in descending order
        if trimmed:
            if not mutable:
                left_intervals = [itvl.copy() for itvl in left_intervals]
                right_intervals = [itvl.copy() for itvl in right_intervals]
        else:
            left_intervals = cls.trim_intervals(left_intervals, mutable=mutable)
            right_intervals = cls.trim_intervals(right_intervals, mutable=mutable)

        itvls = []
        lidx, ridx = 0, 0
        # Check and substract intervals in turn
        while lidx < len(left_intervals) and ridx < len(right_intervals):
            if left_intervals[lidx] < right_intervals[ridx]:
                itvls.append(left_intervals[lidx])
                lidx += 1
            elif right_intervals[ridx] < left_intervals[lidx]:
                ridx += 1
            else:
                tmp_itvl = left_intervals[lidx].remove(right_intervals[ridx], keep_right=True)
                if tmp_itvl:
                    itvls.append(tmp_itvl)
                if not left_intervals[lidx]:
                    lidx += 1
                else:
                    ridx += 1

        # Extend with rest `left_intevals`
        itvls.extend(reversed(left_intervals[lidx:]))
        return itvls

    @classmethod
    def intervals_diff_sized(cls,
        left_intervals:Iterable,
        right_sized:Sized,
        trimmed:bool=False,
        mutable:bool=False
    ) -> list:
        """
        Description:
        Calculate the difference of `left_intervals` from `right_sized`

        Params:
        left_intervals: intervals from which to get difference
        right_intervals: list of points with which to subtract
        trimmed: if `left_intervals` and `right_sized` are trimmed
            1. True: copy each interval directly
            2. False: trim intervals

        Return:
        """
        # Trim intervals
        # P.S.
        # `sized` won't be copied here even if not `mutable` and trimmed, 
        # because `pop` won't be used in this method, which means `sized`
        # won't be altered in this method.
        if trimmed:
            if not mutable:
                left_intervals = [itvl.copy() for itvl in left_intervals]
        else:
            left_intervals = cls.trim_intervals(left_intervals, mutable=mutable)
            right_sized = sorted(right_sized)
        # Create intervals for each elements in `right_sized`
        right_intervals = [Interval.from_single(ele) for ele in right_sized]

        return cls.intervals_diff_intervals(left_intervals, right_intervals, True, True)

    @classmethod
    def sized_diff_intervals(cls,
        left_sized:Iterable,
        right_intervals:Iterable,
        trimmed:bool=False,
        mutable:bool=False
    ) -> list:
        """
        Description:
        Calculate the difference of `left_sized` from `right_intervals`, A.K.A.
        points in `left_sized` that not in `right_intervals`

        Params:
        left_sized
        right_intervals
        trimmed
        mutable

        Return:
        [points in `right_intervals`]
        """
        # Trim intervals
        # P.S.
        # `sized` won't be copied here even if not `mutable` and trimmed, 
        # because `pop` won't be used in this method, which means `sized`
        # won't be altered in this method.
        if trimmed:
            if not mutable:
                right_intervals = [itvl.copy() for itvl in right_intervals]
        else:
            right_intervals = cls.trim_intervals(right_intervals, mutable=mutable)
            left_sized = sorted(left_sized)
        # Create intervals for each elements in `left_sized`
        left_intervals = [Interval.from_single(ele) for ele in left_sized]

        itvls = cls.intervals_diff_intervals(left_intervals, right_intervals, True, True)
        return [itvl.left for itvl in itvls ]

    @classmethod
    def intervals_union_intervals(cls,
        left_intervals:Iterable,
        right_intervals:Iterable,
        trimmed:bool=False,
        mutable:bool=False
    ) -> list:
        """
        Description:
        Join `left_intervals` and `right_intervals`

        Params:
        left_intervals
        right_intervals
        trimmed
        mutable

        Return
        [Union of intervals, ]
        """
        if trimmed:
            itvls = cls.merge_intervals(left_intervals, right_intervals, mutable=mutable)
        else:
            itvls = cls.trim_intervals(left_intervals, right_intervals, mutable=mutable)
        return itvls

    @classmethod
    def intervals_union_sized(cls,
        left_intervals:Iterable,
        right_sized:Iterable,
        trimmed:bool=False,
        mutable:bool=False
    ) -> Tuple[set, list]:
        """
        Description:
        Join `left_intervals` and `right_sized`

        Params:
        left_intervals
        right_sized
        trimmed
        mutable

        Return:
        {points, }, [intervals, ]
        """
        # Trim intervals
        # P.S.
        # `sized` won't be copied here even if not `mutable` and trimmed, 
        # because `pop` won't be used in this method, which means `sized`
        # won't be altered in this method.
        if trimmed:
            if not mutable:
                left_intervals = [itvl.copy() for itvl in left_intervals]
                right_sized = right_sized.copy()
        else:
            left_intervals = cls.trim_intervals(left_intervals, mutable=mutable)
            right_sized = sorted(right_sized)

        # Check if elements in intervals for each element in `sized`
        sized, itvls = set(), []
        lidx, ridx = 0, 0 
        while lidx < len(left_intervals) and ridx < len(right_sized):
            if right_sized[ridx] < left_intervals[lidx].left:
                sized.append(right_sized[ridx])
                ridx += 1
            elif right_sized[ridx] == left_intervals[lidx].left:
                left_intervals[lidx].including_left = True
                ridx += 1
            elif right_sized[ridx] < left_intervals[lidx].right:
                ridx += 1
            elif right_sized[ridx] == left_intervals[lidx].right:
                left_intervals[lidx].including_right = True
                ridx += 1
            else:
                itvls.append(left_intervals[lidx])
                lidx += 1

        # Extend and update with rest
        sized.update(right_sized)
        itvls.extend(left_intervals)

        return sized, itvls

    @classmethod
    def complement_intervals(cls,
        intervals:Iterable,
        trimmed:bool=False,
        mutable:bool=False,
    ) -> list:
        """
        Description:
        Get the complement of `intervals` from universe intervals, (-inf, inf).
        Here `intervals_diff_intervals` with `UNI_INTERVAL` will be called.

        Params:
        intervals
        trimmed
        mutable

        Return:
        [intervals, ]
        """
        return cls.intervals_diff_intervals(
            [UNI_INTERVAL.copy()],
            intervals,
            trimmed,
            mutable
        )


    @classmethod
    def intervals_intersect_intervals(cls,
        left_intervals:Iterable,
        right_intervals:Iterable,
        trimmed:bool=False,
        mutable:bool=False
    ) -> list:
        """
        Description:
        Calculate intersection between `left_intervals` and `right_intervals`.
        Here complement and union will be used to achieve intersection.

        Params:
        left_intervals
        right_intervals
        trimmed
        mutable

        Return:
        [intervals, ]
        """
        complemented = cls.complement_intervals(right_intervals, trimmed, mutable)
        return cls.intervals_union_intervals(left_intervals, complemented, True, True)

    @classmethod
    def intervals_intersect_sized(cls,
        left_intervals:Iterable,
        right_sized:Sized,
        trimmed:bool=False,
        mutable:bool=False
    ) -> set:
        """
        Description:
        Calculate intersection between `left_intervals` and `right_sized`.
        Here difference will be used achieve intersection.

        Params:
        left_intervals
        right_sized
        trimmed
        mutable

        Return:
        {points, }
        """
        # Don't change left and right if keep `trimmed`
        return set(right_sized).difference(
            cls.sized_diff_intervals(left_intervals, right_sized, trimmed, mutable)
        )

    @classmethod
    def from_str(cls, str_:str) -> Interval:
        """
        Description:
        Construct interval from `str_`, which should following the structure
        of its mathimatical expression.

        Params:
        str_: with format "(left, right]"

        Return:
        interval
        """
        itvl = cls()
        str_ = str_.strip()

        # Set if including edge
        if str_[0] == "[":
            itvl.including_left = True
        elif str_[0] == "(":
            itvl.including_left = False
        else:
            raise ValueError(f"Invalid parameter {str_}: interval must start with `(` or `[`")

        if str_[-1] == "]":
            itvl.including_right = True
        elif str_[-1] == ")":
            itvl.including_right = False
        else:
            raise ValueError(f"Invalid parameter {str_}: interval must end with `)` or `]`")

        # Set edge
        itvl.left, itvl.right = map(lambda edge: int(edge), str_[1:-1].split(","))

        return itvl

    @classmethod
    def from_single(cls, single:Union[int, float]) -> Interval:
        """
        Description:
        Create interval containing only one 
        """
        if not single:
            return NAN_INTERVAL
        return cls(single, single, True, True)

    def copy(self):
        """
        Description:
        Copy self
        """
        copy_ = Interval(
            self.left,
            self.right,
            self.including_left,
            self.including_right
        )
        return copy_

    def overlaps(self, other:Any, adjoined=True) -> bool:
        """
        Descripion:
        Check if `self` overlaps `other`

        Params:
        other: Interval, list, set, int, etc
        adjoined: If regarding two adjoined intervals as overlaping

        Return:
        if `self` overlaps `other`
        """
        # Boundary cases
        # If `other` is null, return False directly
        if not other:
            return False

        if (not self > other) and (not self < other):
            return True
        elif issubclass(type(other), self.__class__) and adjoined:
            if (self.including_left or other.including_right) and \
                self.left == other.right:
                return True
            if (self.including_right or other.including_left) and \
                self.right == other.left:
                return True
        else:
            return False

    def extend(self, other: Interval) -> Interval:
        """
        Description:
        Extend self's span with another interval `other`
        1. `self` overlaps `other`: extend `self` and return `NAN_INTERVAL`
        2. `self` doesn't overlap `other`: return `other` directly

        Parameters:
        other: intervals

        Return:
        `other` or `NAN_INTERVAL`
        """
        if self.overlaps(other):
            if other.max() > self.max():
                self.right = other.right
                self.including_right = other.including_right
            if other.min() < self.min():
                self.left = other.left
                self.including_left = other.including_left
            return NAN_INTERVAL
        else:
            return other

    def remove(self,
        other:Interval,
        keep_right:Union[bool, None]=None
    ) -> Interval:
        if (keep_right is None) or keep_right:
            # Set temperary left-side interval
            tmp_itvl = Interval(
                self.left,
                other.left,
                self.including_left,
                not other.including_left
            )
            if not tmp_itvl:
                tmp_itvl = NAN_INTERVAL
            # Right-side prefered
            self.left = other.right
            self.including_left = not other.including_right

            # Set `self` with not null side, right-side prefered
            if (keep_right is None) and (not self):
                self.set_with(tmp_itvl)
                return NAN_INTERVAL
            # Set `self` with right-side at all time
            # Return left-side at all time
            else:
                return tmp_itvl

        # Set `self` with left-side at all time
        # Return right-side at all time
        else:
            # Set temperary left-side interval
            tmp_itvl = Interval(
                other.right,
                self.right,
                not other.including_right,
                self.including_right
            )
            if not tmp_itvl:
                tmp_itvl = NAN_INTERVAL
            # Left-side prefered
            self.right = other.left
            self.including_right = not other.including_left
            return tmp_itvl

    def set_with(self, other: Interval) -> None:
        """
        Description:
        Set `self` with `other`, A.K.A. copying `other` as `self`

        Params:
        other

        Return:
        """
        self.left, self.right = other.left, other.right
        self.including_left, self.including_right = other.including_left, other.including_right

    def clear(self) -> None:
        """
        Description:
        Set `self` with `NAN_INTERVAL`, A.K.A. copying `NAN_INTERVAL` as `self`
        """
        self.set_with(NAN_INTERVAL)


INF = float("inf")
NINF = float("-inf")
NAN = float("nan")
UNI_INTERVAL = Interval(NINF, INF, False, False)
MAX_INTERVAL = Interval(INF, INF, False, False)
MIN_INTERVAL = Interval(NINF, NINF, False, False)
NAN_INTERVAL = Interval(NAN, NAN, False, False)
# %%
class Value(Iterable):
    def __init__(
        self,
        value:Any=[],
        trimmed:bool=False,
        mutable:bool=False
    ):
        """
        Description:
        Struct managing intervals and points together.

        P.S.
        Iterable will be flattened.

        Params:
        value: [int, float, intervals, etc]
        trimmed: if elements in `value` are trimmed
        mutable: if elements in `value` are mutable, for intervals especially
        """
        value = flatten_iterable(value)
        intervals, sized = separate_container(value)
        sized, intervals = Interval.intervals_union_sized(
            intervals,
            size,
            trimmed,
            mutable
        )
        self.intervals = intervals
        self.sized = sized

    def __contains__(self, item:Any, closed:bool=False) -> bool:
        # Use flag to record if every elements in `item` is contained
        if_contained = True
        # If `item` is not iterable, traverse to check if `self` contains it
        if not issubclass(type(item), Iterable):
            for inner_ele in self:
                if item in inner_ele:
                    break
            else:
                if_contained = False
        # Else, traverse `item` to check if `self` contains each element
        # recursively
        else:
            for outer_ele in item:
                # Check if containing recurrsively
                if outer_ele not in self:
                    if_contained = False
                    break
        return if_contained

    def __iter__(self) -> Iterator:
        """
        Description:
        `self.sized` and each intervals in `self.intervals` will be
        yield in order.
        """
        yield self.sized
        yield from self.intervals

    def __repr__(self) -> str:
        """
        Description:
        `self` will be represented as `{sized},interval,...`
        """
        sized_str = ','.join([repr(ele) for ele in self.sized])
        itvls_str = ','.join([repr(itvl) for itvl in self.intervals])
        return f"{{{sized_str},{itvls_str}}}"

    def max(self) -> bool:
        """
        Description:
        Return the maximum.
        """
        return max(max(self.sized), max([itvl.max() for itvl in self.intervals]))

    def min(self) -> bool:
        """
        Return the minimum.
        """
        return min(min(self.sized), min([itvl.min() for itvl in self.intervals]))

    def __lt__(self, other: Any) -> bool:
        return self.max() < other

    def __gt__(self, other: Any) -> bool:
        return self.min() > other

    def __eq__(self, other: Any) -> bool:
        return (self in other) and (other in self)

    def __add__(self, other:Any, mutable:bool=False) -> Value:
        # Copy `self` if not mutable
        if not mutable:
            self_copy = self.copy
        else:
            self_copy = self

        if issubclass(type(other), Iterable):
            # Seperate and sort intervals and sized
            other = flatten_iterable(other)
            itvls, sized = separate_container(other)
            self_copy.sized.update(sized)
            sized = sorted(self_copy.sized)
            itvls = Interval.trim_intervals(itvls, mutable=mutable)
            itvls = Interval.merge_intervals(
                self_copy.intervals,
                itvls,
                mutable=True
            )
        else:
            if issubclass(type(other), Interval):
                # P.S.
                # Here `.merge_intervals` works like ordering insertation,
                #  and some insertation can be more efficient, but lazyness.
                other = other if mutable else other.copy()
                itvls = Interval.merge_intervals(
                    self_copy.intervals,
                    [other],
                    mutable=True
                )
                sized = self_copy.sized
            else:
                itvls = self_copy.intervals
                self.sized.add(other)
                sized = self.sized

        # Trim intervals with sized
        sized, intervals = Interval.intervals_union_sized(
            itvls,
            sized,
            True,
            True
        )

        self_copy.sized, self_copy.intervals = sized, intervals
        return self_copy

    def __sub__(self, other:Any, mutable:bool=False) -> Value:
        # Copy `self` if not mutable
        if not mutable:
            self_copy = self.copy()
        else:
            self_copy = self

        if issubclass(type(other), Iterable):
            # Seperate and sort intervals and sized
            other = flatten_iterable(other)
            itvls, sized = separate_container(other)
            sized = sorted(sized)
            itvls = Interval.trim_intervals(itvls, mutable=mutable)
            self_copy.sized = self_copy.sized.difference(sized)
            self_copy.sized = Interval.sized_diff_intervals(
                sorted(self_copy.sized),
                itvls,
                True,
                True
            )
            self_copy.intervals = Interval.intervals_union_sized(
                self_copy.intervals,
                itvls,
                True,
                True
            )
        else:
            if issubclass(type(other), Interval):
                other = other if mutable else other.copy()
                self_copy.sized = Interval.sized_diff_intervals(
                    sorted(self_copy.sized),
                    [other, ],
                    True,
                    True
                )
                self_copy.intervals = Interval.intervals_diff_intervals(
                    self_copy.intervals,
                    [other, ],
                    True,
                    True
                )
            else:
                self_copy.sized = self_copy.sized.difference(other)
                self_copy.intervals = Interval.intervals_diff_sized(
                    self_copy.intervals,
                    [other, ],
                    True,
                    True
                )

        return self_copy


    def copy(self) -> Value:
        """
        Description:
        Return a copy of self.
        """
        return self.__class__.from_raw(
            self.sized.copy(),
            [itvl.copy() for itvl in self.intervals]
        )

    def set_with(self, other:Value) -> None:
        """
        Description:
        Set `self` with `other`, A.K.A. copying `other` as `self`.

        Params:
        other

        Return:
        """
        self.sized = other.sized.copy()
        self.intervals = [itvl.copy() for itvl in other.intervals]

    def overlaps(self, other: Any):
        pass

    @classmethod
    def from_raw(cls, sized:set, intervals:list) -> Value:
        """
        Description:
        Create `Value` with given `sized` and `intervals`.
        1. No additional check will be applied, which means that returned
           `Value` may be invalid.

        Params:
        sized
        intervals

        Return:
        Value
        """
        inst = cls()
        inst.sized = sized
        inst.intervals = intervals
        return inst

    @classmethod
    def from_str(cls, str_:str) -> Value:
        """
        Description:
        Construct `Value` from string.

        Params:
        str_: with format like that: "{{}, (left, right],...}"

        Return:
        """
        str_ = str_.repalce(" ", "")[1:-1]
        sized_str, itvls_str = str_.split("},")
        sized_str = sized[1:].split(",")
        sized_idx = 0
        for sized_idx in range(len(sized_str)):
            if re.fullmatch("[+-]?\d+", sized_str[sized_idx]):
                sized_str[sized_idx] = int(sized_str[sized_idx])
            else:
                sized_str[sized_idx] = float(sized_str[sized_idx])
        itvls, itvl_idx = [], 0
        itvls_str = itvls_str.split(",")
        while itvl_idx < len(itvls_str):
            itvls.append(Interval.from_str(f"{itvls_str[itvl_idx]},{itvls_str[itvl_idx+1]}"))
            itvl_idx += 2
        return Value.from_raw(
            set(sized),
            itvls
        )
# %%
if __name__ == "__main__":
    a = Interval(1, 2)
    b = Interval(2, 5)
    c = Interval(5.5, 6)
    d = Interval(7, 20)
    print(Interval.intervals_diff_intervals([b, d, c, a], [c]))
    print(Interval.complement_intervals([a, b, c, d]))
    print(Interval.intervals_diff_intervals([UNI_INTERVAL], [a, b, c, d]))
    Interval.trim_intervals([b, d, c, a], True)


# %%
