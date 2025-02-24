"""Utilities for filtering or searching :class:`list` of objects / list data.

Note
----
This is an internal API not covered by versioning policy.
"""
import re
import traceback
from collections.abc import Mapping, Sequence
from re import Pattern
from typing import Any, Callable, Optional, Protocol, TypeVar, Union

T = TypeVar("T", Any, Any)


def keygetter(
    obj: Mapping[str, Any],
    path: str,
) -> Union[None, Any, str, list[str], Mapping[str, str]]:
    """Fetch values in objects and keys, supported nested data.

    **With dictionaries**:

    >>> keygetter({ "food": { "breakfast": "cereal" } }, "food")
    {'breakfast': 'cereal'}

    >>> keygetter({ "food": { "breakfast": "cereal" } }, "food__breakfast")
    'cereal'

    **With objects**:

    >>> from typing import Optional
    >>> from dataclasses import dataclass, field

    >>> @dataclass()
    ... class Food:
    ...     fruit: list[str] = field(default_factory=list)
    ...     breakfast: Optional[str] = None


    >>> @dataclass()
    ... class Restaurant:
    ...     place: str
    ...     city: str
    ...     state: str
    ...     food: Food = field(default_factory=Food)


    >>> restaurant = Restaurant(
    ...     place="Largo",
    ...     city="Tampa",
    ...     state="Florida",
    ...     food=Food(
    ...         fruit=["banana", "orange"], breakfast="cereal"
    ...     )
    ... )

    >>> restaurant
    Restaurant(place='Largo',
        city='Tampa',
        state='Florida',
        food=Food(fruit=['banana', 'orange'], breakfast='cereal'))

    >>> keygetter(restaurant, "food")
    Food(fruit=['banana', 'orange'], breakfast='cereal')

    >>> keygetter(restaurant, "food__breakfast")
    'cereal'
    """
    try:
        sub_fields = path.split("__")
        dct = obj
        for sub_field in sub_fields:
            if isinstance(dct, dict):
                dct = dct[sub_field]
            elif hasattr(dct, sub_field):
                dct = getattr(dct, sub_field)
        return dct
    except Exception as e:
        traceback.print_stack()
        print(f"Above error was {e}")
    return None


def parse_lookup(obj: Mapping[str, Any], path: str, lookup: str) -> Optional[Any]:
    """Check if field lookup key, e.g. "my__path__contains" has comparator, return val.

    If comparator not used or value not found, return None.

    >>> parse_lookup({ "food": "red apple" }, "food__istartswith", "__istartswith")
    'red apple'

    It can also look up objects:

    >>> from dataclasses import dataclass

    >>> @dataclass()
    ... class Inventory:
    ...     food: str

    >>> item = Inventory(food="red apple")

    >>> item
    Inventory(food='red apple')

    >>> parse_lookup(item, "food__istartswith", "__istartswith")
    'red apple'
    """
    try:
        if isinstance(path, str) and isinstance(lookup, str) and path.endswith(lookup):
            if field_name := path.rsplit(lookup)[0]:
                return keygetter(obj, field_name)
    except Exception:
        traceback.print_stack()
    return None


class LookupProtocol(Protocol):
    """Protocol for :class:`QueryList` filtering operators."""

    def __call__(
        self,
        data: Union[str, list[str], Mapping[str, str]],
        rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
    ) -> bool:
        """Callback for :class:`QueryList` filtering operators."""
        ...


def lookup_exact(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    return rhs == data


def lookup_iexact(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if not isinstance(rhs, str) or not isinstance(data, str):
        return False

    return rhs.lower() == data.lower()


def lookup_contains(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if not isinstance(rhs, str) or not isinstance(data, (str, Mapping, list)):
        return False

    return rhs in data


def lookup_icontains(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if not isinstance(rhs, str) or not isinstance(data, (str, Mapping, list)):
        return False

    if isinstance(data, str):
        return rhs.lower() in data.lower()
    if isinstance(data, Mapping):
        return rhs.lower() in [k.lower() for k in data.keys()]

    return False


def lookup_startswith(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if not isinstance(rhs, str) or not isinstance(data, str):
        return False

    return data.startswith(rhs)


def lookup_istartswith(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if not isinstance(rhs, str) or not isinstance(data, str):
        return False

    return data.lower().startswith(rhs.lower())


def lookup_endswith(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if not isinstance(rhs, str) or not isinstance(data, str):
        return False

    return data.endswith(rhs)


def lookup_iendswith(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if not isinstance(rhs, str) or not isinstance(data, str):
        return False
    return data.lower().endswith(rhs.lower())


def lookup_in(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if isinstance(rhs, list):
        return data in rhs

    try:
        if isinstance(rhs, str) and isinstance(data, Mapping):
            return rhs in data
        if isinstance(rhs, str) and isinstance(data, (str, list)):
            return rhs in data
        if isinstance(rhs, str) and isinstance(data, Mapping):
            return rhs in data
        # TODO: Add a deep Mappingionary matcher
        # if isinstance(rhs, Mapping) and isinstance(data, Mapping):
        #     return rhs.items() not in data.items()
    except Exception:
        return False
    return False


def lookup_nin(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if isinstance(rhs, list):
        return data not in rhs

    try:
        if isinstance(rhs, str) and isinstance(data, Mapping):
            return rhs not in data
        if isinstance(rhs, str) and isinstance(data, (str, list)):
            return rhs not in data
        if isinstance(rhs, str) and isinstance(data, Mapping):
            return rhs not in data
        # TODO: Add a deep Mappingionary matcher
        # if isinstance(rhs, Mapping) and isinstance(data, Mapping):
        #     return rhs.items() not in data.items()
    except Exception:
        return False
    return False


def lookup_regex(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if isinstance(data, (str, bytes, re.Pattern)) and isinstance(rhs, (str, bytes)):
        return bool(re.search(rhs, data))
    return False


def lookup_iregex(
    data: Union[str, list[str], Mapping[str, str]],
    rhs: Union[str, list[str], Mapping[str, str], Pattern[str]],
) -> bool:
    if isinstance(data, (str, bytes, re.Pattern)) and isinstance(rhs, (str, bytes)):
        return bool(re.search(rhs, data, re.IGNORECASE))
    return False


LOOKUP_NAME_MAP: Mapping[str, LookupProtocol] = {
    "eq": lookup_exact,
    "exact": lookup_exact,
    "iexact": lookup_iexact,
    "contains": lookup_contains,
    "icontains": lookup_icontains,
    "startswith": lookup_startswith,
    "istartswith": lookup_istartswith,
    "endswith": lookup_endswith,
    "iendswith": lookup_iendswith,
    "in": lookup_in,
    "nin": lookup_nin,
    "regex": lookup_regex,
    "iregex": lookup_iregex,
}


class QueryList(list[T]):
    """Filter list of object/dictionaries. For small, local datasets.

    *Experimental, unstable*.

    **With dictionaries**:

    >>> query = QueryList(
    ...     [
    ...         {
    ...             "place": "Largo",
    ...             "city": "Tampa",
    ...             "state": "Florida",
    ...             "foods": {"fruit": ["banana", "orange"], "breakfast": "cereal"},
    ...         },
    ...         {
    ...             "place": "Chicago suburbs",
    ...             "city": "Elmhurst",
    ...             "state": "Illinois",
    ...             "foods": {"fruit": ["apple", "cantelope"], "breakfast": "waffles"},
    ...         },
    ...     ]
    ... )

    >>> query.filter(place="Chicago suburbs")[0]['city']
    'Elmhurst'
    >>> query.filter(place__icontains="chicago")[0]['city']
    'Elmhurst'
    >>> query.filter(foods__breakfast="waffles")[0]['city']
    'Elmhurst'
    >>> query.filter(foods__fruit__in="cantelope")[0]['city']
    'Elmhurst'
    >>> query.filter(foods__fruit__in="orange")[0]['city']
    'Tampa'

    >>> query.filter(foods__fruit__in="apple")
    [{'place': 'Chicago suburbs',
        'city': 'Elmhurst',
        'state': 'Illinois',
        'foods':
            {'fruit': ['apple', 'cantelope'], 'breakfast': 'waffles'}}]

    >>> query.filter(foods__fruit__in="non_existent")
    []

    **With objects**:

    >>> from typing import Any
    >>> from dataclasses import dataclass, field

    >>> @dataclass()
    ... class Restaurant:
    ...     place: str
    ...     city: str
    ...     state: str
    ...     foods: dict[str, Any]

    >>> restaurant = Restaurant(
    ...     place="Largo",
    ...     city="Tampa",
    ...     state="Florida",
    ...     foods={
    ...         "fruit": ["banana", "orange"], "breakfast": "cereal"
    ...     }
    ... )

    >>> restaurant
    Restaurant(place='Largo',
        city='Tampa',
        state='Florida',
        foods={'fruit': ['banana', 'orange'], 'breakfast': 'cereal'})

    >>> query = QueryList([restaurant])

    >>> query.filter(foods__fruit__in="banana")
    [Restaurant(place='Largo',
        city='Tampa',
        state='Florida',
        foods={'fruit': ['banana', 'orange'], 'breakfast': 'cereal'})]

    >>> query.filter(foods__fruit__in="banana")[0].city
    'Tampa'

    **With objects (nested)**:

    >>> from typing import Optional
    >>> from dataclasses import dataclass, field

    >>> @dataclass()
    ... class Food:
    ...     fruit: list[str] = field(default_factory=list)
    ...     breakfast: Optional[str] = None


    >>> @dataclass()
    ... class Restaurant:
    ...     place: str
    ...     city: str
    ...     state: str
    ...     food: Food = field(default_factory=Food)


    >>> query = QueryList([
    ...     Restaurant(
    ...         place="Largo",
    ...         city="Tampa",
    ...         state="Florida",
    ...         food=Food(
    ...             fruit=["banana", "orange"], breakfast="cereal"
    ...         )
    ...     ),
    ...     Restaurant(
    ...         place="Chicago suburbs",
    ...         city="Elmhurst",
    ...         state="Illinois",
    ...         food=Food(
    ...             fruit=["apple", "cantelope"], breakfast="waffles"
    ...         )
    ...     )
    ... ])

    >>> query.filter(food__fruit__in="banana")
    [Restaurant(place='Largo',
        city='Tampa',
        state='Florida',
        food=Food(fruit=['banana', 'orange'], breakfast='cereal'))]

    >>> query.filter(food__fruit__in="banana")[0].city
    'Tampa'

    >>> query.filter(food__breakfast="waffles")
    [Restaurant(place='Chicago suburbs',
        city='Elmhurst',
        state='Illinois',
        food=Food(fruit=['apple', 'cantelope'], breakfast='waffles'))]

    >>> query.filter(food__breakfast="waffles")[0].city
    'Elmhurst'

    >>> query.filter(food__breakfast="non_existent")
    []
    """

    data: Sequence[T]
    pk_key: Optional[str]

    def items(self) -> list[T]:
        data: Sequence[T]

        if self.pk_key is None:
            raise Exception("items() require a pk_key exists")
        return [(getattr(item, self.pk_key), item) for item in self]

    def __eq__(
        self,
        other: object,
        # other: Union[
        #     "QueryList[T]",
        #     List[Mapping[str, str]],
        #     List[Mapping[str, int]],
        #     List[Mapping[str, Union[str, Mapping[str, Union[List[str], str]]]]],
        # ],
    ) -> bool:
        data = other

        if not isinstance(self, list) or not isinstance(data, list):
            return False

        if len(self) == len(data):
            for (a, b) in zip(self, data):
                if isinstance(a, Mapping):
                    a_keys = a.keys()
                    if a.keys == b.keys():
                        for key in a_keys:
                            if abs(a[key] - b[key]) > 1:
                                return False
                else:
                    if a != b:
                        return False

            return True
        return False

    def filter(
        self, matcher: Optional[Union[Callable[[T], bool], T]] = None, **kwargs: Any
    ) -> "QueryList[T]":
        def filter_lookup(obj: Any) -> bool:
            for path, v in kwargs.items():
                try:
                    lhs, op = path.rsplit("__", 1)

                    if op not in LOOKUP_NAME_MAP:
                        raise ValueError(f"{op} not in LOOKUP_NAME_MAP")
                except ValueError:
                    lhs = path
                    op = "exact"

                assert op in LOOKUP_NAME_MAP
                path = lhs
                data = keygetter(obj, path)

                if data is None or not LOOKUP_NAME_MAP[op](data, v):
                    return False

            return True

        if callable(matcher):
            _filter = matcher
        elif matcher is not None:

            def val_match(obj: Union[str, list[Any]]) -> bool:
                if isinstance(matcher, list):
                    return obj in matcher
                else:
                    return obj == matcher

            _filter = val_match
        else:
            _filter = filter_lookup

        return self.__class__(k for k in self if _filter(k))
