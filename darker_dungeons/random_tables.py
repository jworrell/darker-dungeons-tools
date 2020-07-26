import random
from typing import List, Dict, Any, Optional

from darker_dungeons.character import CharacterChoice


class RandomTable:
    @staticmethod
    def from_list(_list: List[Dict[str, Any]], die_size: Optional[int] = None) -> 'RandomTable':
        choices = []

        for item in _list:
            choices.append(RandomTableOption.from_dict(item))

        return RandomTable(choices, die_size)

    def __init__(self, choices: List['RandomTableOption'], die_size: Optional[int] = None) -> None:
        choices.sort(key=lambda choice: choice.low)

        self.choices = choices

        if die_size is None:
            die_size = self.choices[-1].high

        self.die_size = die_size

        self.validate()

    def validate(self) -> bool:
        for m, n in zip(self.choices[:-1], self.choices[1:]):
            if m.high + 1 != n.low:
                raise ValueError("this.high + 1 != next.low")

        if self.choices[-1].high != self.die_size:
            raise ValueError("self.choices[-1].last != self.die_size")

        return True

    def _choose(self) -> List['RandomTableOption']:
        roll = random.randint(1, self.die_size)

        for choice in self.choices:
            if choice.low <= roll <= choice.high:
                choice_chain = [choice]

                if choice.subtable:
                    choice_chain += choice.subtable._choose()

                return choice_chain

        raise ValueError("Failed to find choice, this shouldbn't happen")

    def choose(self) -> CharacterChoice:
        choice_chain = self._choose()

        return CharacterChoice(
            choice=choice_chain[0].value,
            subchoice=None if len(choice_chain) < 2 else choice_chain[1].value,
        )


class RandomTableOption:
    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> 'RandomTableOption':
        return RandomTableOption(
            low=int(_dict["roll"][0]),
            high=int(_dict["roll"][1]),
            value=_dict["value"],
            subtable=RandomTable.from_list(_dict["subtable"]) if "subtable" in _dict else None,
        )

    def __init__(self, low: int, high: int, value: str, subtable: Optional[RandomTable] = None):
        self.low = low
        self.high = high
        self.value = value
        self.subtable = subtable
