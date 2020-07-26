"""
Simple API for rolling new characters
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

import yaml


@dataclass
class CharacterStats:
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    @staticmethod
    def roll_stat() -> int:
        return sum(random.randint(1, 6) for _ in range(3))

    @staticmethod
    def roll_stats() -> 'CharacterStats':
        return CharacterStats(
            strength=CharacterStats.roll_stat(),
            dexterity=CharacterStats.roll_stat(),
            constitution=CharacterStats.roll_stat(),
            intelligence=CharacterStats.roll_stat(),
            wisdom=CharacterStats.roll_stat(),
            charisma=CharacterStats.roll_stat(),
        )


@dataclass
class CharacterChoice:
    choice: str
    subchoice: Optional[str]


@dataclass
class Character:
    race: CharacterChoice
    background: CharacterChoice
    _class: CharacterChoice
    reroll: int
    rolled_stats: CharacterStats
    suggested_stats: Optional[CharacterStats]

    def suggest_stats(self):
        rolled_stats = asdict(self.rolled_stats)

        worst_stat = min((v, k) for k, v in rolled_stats.items())

        print(rolled_stats, worst_stat, self.reroll)

        if worst_stat[0] < self.reroll:
            rolled_stats[worst_stat[1]] = self.reroll

        best_stat = max((v, k) for k, v in rolled_stats.items())


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


def get_base_headers(content_length: int) -> Dict[str, str]:
    return {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
        "Content-Length": str(content_length),
    }


def lambda_init() -> Tuple[RandomTable, RandomTable, RandomTable]:
    backgrounds = yaml.load(open("tables/background.yml"), Loader=yaml.BaseLoader)
    background_table = RandomTable.from_list(backgrounds, 100)

    classes = yaml.load(open("tables/class.yml"), Loader=yaml.BaseLoader)
    class_table = RandomTable.from_list(classes)

    races = yaml.load(open("tables/race.yml"), Loader=yaml.BaseLoader)
    race_table = RandomTable.from_list(races, 100)

    return background_table, class_table, race_table


BACKGROUND_TABLE, CLASS_TABLE, RACE_TABLE = lambda_init()


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    rolled_stats = CharacterStats.roll_stats()

    character = Character(
        race=RACE_TABLE.choose(),
        background=BACKGROUND_TABLE.choose(),
        _class=CLASS_TABLE.choose(),
        reroll=CharacterStats.roll_stat(),
        rolled_stats=rolled_stats,
        suggested_stats=None,
    )

    character.suggest_stats()

    result = json.dumps(asdict(character))

    return {
        "statusCode": 200,
        "headers": get_base_headers(len(result)),
        "body": result,
    }


if __name__ == "__main__":
    print(lambda_handler({}, {}))
