import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Mapping, Sequence, TypeVar, Generic, Set


@dataclass
class RandomTableValue:
    name: str

    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> 'RandomTableValue':
        return RandomTableValue(
            name=_dict["name"]
        )

    def flatten(self):
        return f"{self.name}"


@dataclass
class RandomAgeTableValue(RandomTableValue):
    memories: int

    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> 'RandomTableValue':
        raw_memories = _dict.get("memories", None)
        memories = 0 if raw_memories is None else int(raw_memories)

        return RandomAgeTableValue(
            name=_dict["name"],
            memories=memories,
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


@dataclass
class RandomDescribedTableValue(RandomTableValue):
    description: str

    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> 'RandomTableValue':
        return RandomDescribedTableValue(
            name=_dict["name"],
            description=_dict.get("description", None),
        )

    def flatten(self):
        return f"{self.name}: {self.description}"


TABLE_VALUE_CLASSES: Dict[Optional[str], Any] = {
    "RandomTableValue": RandomTableValue,
    "RandomAgeTableValue": RandomAgeTableValue,
    "RandomClassTableValue": RandomClassTableValue,
    "RandomDescribedTableValue": RandomDescribedTableValue,
}

T = TypeVar("T", bound=RandomTableValue)


def flatten_selections(selections: Mapping[str, T]) -> Mapping[str, Any]:
    flat_dict: Dict[str, str] = {}

    for key, selection in selections.items():
        selection_dict = asdict(selection)

        flat_dict[key] = selection_dict["name"]

        for inner_key, inner_item in selection_dict.items():
            if inner_key == "name":
                continue

            if inner_item is not None:
                flat_dict[inner_key] = inner_item

    return flat_dict


def flatten_selections_more(selections: Mapping[str, T]) -> str:
    if len(selections) > 1:
        raise ValueError("Can't flatten_selections_mode on long dict")

    for _, selection in selections.items():
        return selection.flatten()

    raise ValueError("selections was empty")


class RandomTableItem(Generic[T]):
    @staticmethod
    def from_dict(value_class, _dict: Dict[str, Any]) -> 'RandomTableItem[T]':
        return RandomTableItem(
            low=int(_dict["roll"][0]),
            high=int(_dict["roll"][1]),
            value=value_class.from_dict(_dict["value"]),
            subtables=[RandomTable.from_dict(item, parent_value_class=value_class)
                       for item in _dict.get("subtables", [])],
        )

    def __init__(self, low: int, high: int, value: T, subtables: Sequence['RandomTable[T]']) -> None:
        self.low = low
        self.high = high
        self.value = value
        self.subtables = subtables


class RandomTable(Generic[T]):
    @staticmethod
    def from_dict(_dict: Dict[str, Any], die_size: Optional[int] = None, parent_value_class=None) -> 'RandomTable[T]':
        if parent_value_class is None:
            parent_value_class = RandomTableValue

        value_class = TABLE_VALUE_CLASSES.get(_dict.get("value_class"), parent_value_class)

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

    def choose_many(self, count: int) -> List[Mapping[str, T]]:
        choices: List[Mapping[str, T]] = []
        flat_choices: Set[str] = set()

        max_iterations = 25

        for _ in range(max_iterations):
            choice = self.choose()
            flat_choice = flatten_selections_more(choice)

            if flat_choice in flat_choices:
                continue
            else:
                flat_choices.add(flat_choice)

            if len(choices) == count:
                return choices

            elif len(choices) > count:
                raise ValueError("len(choices) > count, this can't happen")

        return choices
