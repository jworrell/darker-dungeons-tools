import random
from typing import List, Dict, Any, Optional, Mapping, Sequence, TypeVar, Generic


class RandomTableValue:
    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> 'RandomTableValue':
        return RandomTableValue(
            name=_dict["name"]
        )

    def __init__(self, name):
        self.name = name


T = TypeVar("T", bound=RandomTableValue)


class RandomTableItem(Generic[T]):
    @staticmethod
    def from_dict(value_class, _dict: Dict[str, Any]) -> 'RandomTableItem':
        return RandomTableItem(
            low=int(_dict["roll"][0]),
            high=int(_dict["roll"][1]),
            value=value_class.from_dict(_dict["value"]),
            subtables=[RandomTable.from_dict(value_class, item) for item in _dict.get("subtables", [])],
        )

    def __init__(self, low: int, high: int, value: T, subtables: Sequence['RandomTable']) -> None:
        self.low = low
        self.high = high
        self.value = value
        self.subtables = subtables


class RandomTable(Generic[T]):
    @staticmethod
    def from_dict(value_class, _dict: Dict[str, Any], die_size: Optional[int] = None) -> 'RandomTable':
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
                selected_items[self.name] = item.value.name

                for subtable in item.subtables:
                    subtable._choose(selected_items)

                return

        raise ValueError("Failed to find item, this shouldn't happen")

    def choose(self) -> Mapping[str, T]:
        selected_items: Dict[str, T] = {}

        self._choose(selected_items)

        return selected_items
