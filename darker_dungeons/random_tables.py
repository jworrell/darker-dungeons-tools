import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Mapping, Sequence, TypeVar, Generic


@dataclass
class RandomTableValue:
    name: str

    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> 'RandomTableValue':
        return RandomTableValue(
            name=_dict["name"]
        )


@dataclass
class RandomClassTableValue(RandomTableValue):
    preferred_stats: List[str]

    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> 'RandomTableValue':
        return RandomClassTableValue(
            name=_dict["name"],
            preferred_stats=_dict.get("preferred_stats", None),
        )


TABlE_VALUE_CLASSES = {
    "RandomTableValue": RandomTableValue,
    "RandomClassTableValue": RandomClassTableValue,
}

T = TypeVar("T", bound=RandomTableValue)


def flatten_selections(selections: Mapping[str, T]) -> Mapping[str, str]:
    flat_dict: Dict[str, str] = {}

    for key, selection in selections.items():
        selection_dict = asdict(selection)

        flat_dict[key] = selection_dict["name"]

        for inner_key, inner_item in selection_dict.items():
            if inner_key == "name":
                continue

            flat_dict[inner_key] = inner_item

    return flat_dict


class RandomTableItem(Generic[T]):
    @staticmethod
    def from_dict(value_class, _dict: Dict[str, Any]) -> 'RandomTableItem[T]':
        return RandomTableItem(
            low=int(_dict["roll"][0]),
            high=int(_dict["roll"][1]),
            value=value_class.from_dict(_dict["value"]),
            subtables=[RandomTable.from_dict(item) for item in _dict.get("subtables", [])],
        )

    def __init__(self, low: int, high: int, value: T, subtables: Sequence['RandomTable[T]']) -> None:
        self.low = low
        self.high = high
        self.value = value
        self.subtables = subtables


class RandomTable(Generic[T]):
    @staticmethod
    def from_dict(_dict: Dict[str, Any], die_size: Optional[int] = None) -> 'RandomTable[T]':
        value_class_name = _dict.get("value_class", "RandomTableValue")
        value_class = TABlE_VALUE_CLASSES.get(value_class_name)

        if value_class is None:
            raise ValueError("Invalid value_class provided in random table")

        items: List[RandomTableItem[T]] = []

        for item in _dict["items"]:
            items.append(RandomTableItem.from_dict(value_class, item))

        return RandomTable(_dict["table"], items, die_size)

    def __init__(self, name: str, items: Sequence[RandomTableItem[T]], die_size: Optional[int] = None) -> None:
        self.name = name
        self.items: Sequence[RandomTableItem[T]] = sorted(items, key=lambda item: item.low)

        if die_size is None:
            die_size = self.items[-1].high

        self.die_size = die_size

        self.validate()

    def validate(self) -> bool:
        for m, n in zip(self.items[:-1], self.items[1:]):
            if m.high + 1 != n.low:
                raise ValueError("this.high + 1 != next.low")

        if self.items[-1].high != self.die_size:
            raise ValueError("self.items[-1].last != self.die_size")

        return True

    def _choose(self, selected_items: Dict[str, T]) -> None:
        """
        Mutates selected_items (does not return anything)!
        """

        roll = random.randint(1, self.die_size)

        for item in self.items:
            if item.low <= roll <= item.high:
                selected_items[self.name] = item.value

                for subtable in item.subtables:
                    subtable._choose(selected_items)

                return

        raise ValueError("Failed to find item, this shouldn't happen")

    def choose(self) -> Mapping[str, T]:
        selected_items: Dict[str, T] = {}

        self._choose(selected_items)

        return selected_items
