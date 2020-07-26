"""
Simple API for rolling new characters
"""

import random
import json
from typing import Dict, List, Any, Optional, Tuple

import yaml


def roll_stat() -> int:
    return sum(random.randint(1, 6) for _ in range(3))


def roll_stats() -> Dict[str, int]:
    return {
        "Strength": roll_stat(),
        "Dexterity": roll_stat(),
        "Constitution": roll_stat(),
        "Intelligence": roll_stat(),
        "Wisdom": roll_stat(),
        "Charisma": roll_stat(),
        "Reroll": roll_stat(),
    }


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

    def choose(self) -> List['RandomTableOption']:
        roll = random.randint(1, self.die_size)

        for choice in self.choices:
            if choice.low <= roll <= choice.high:
                chain = [choice]

                if choice.subtable:
                    chain += choice.subtable.choose()

                return chain

        raise ValueError("Failed to find choice, this shouldbn't happen")


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


def format_choice(choice: List[RandomTableOption]) -> str:
    if len(choice) == 1:
        return f"{choice[0].value}"

    elif len(choice) == 2:
        return f"{choice[0].value} ({choice[1].value})"

    else:
        raise ValueError("Don't know how to format choice")


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
    result = json.dumps({
        "race": format_choice(RACE_TABLE.choose()),
        "background": format_choice(BACKGROUND_TABLE.choose()),
        "class": format_choice(CLASS_TABLE.choose()),
        "stats": roll_stats(),
    })

    return {
        "statusCode": 200,
        "headers": get_base_headers(len(result)),
        "body": result,
    }


if __name__ == "__main__":
    print(lambda_handler({}, {}))
