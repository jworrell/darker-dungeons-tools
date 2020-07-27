"""
Simple API for rolling new characters
"""

import json
from dataclasses import asdict
from typing import Dict, Any, Tuple

import yaml

from darker_dungeons.character import CharacterStats, Character
from darker_dungeons.random_tables import RandomTable, RandomTableValue


def get_base_headers(content_length: int) -> Dict[str, str]:
    return {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
        "Content-Length": str(content_length),
    }


def lambda_init() -> Tuple[RandomTable, RandomTable, RandomTable]:
    backgrounds = yaml.load(open("tables/background.yml"), Loader=yaml.BaseLoader)
    background_table = RandomTable.from_dict(RandomTableValue, backgrounds, 100)

    classes = yaml.load(open("tables/class.yml"), Loader=yaml.BaseLoader)
    class_table = RandomTable.from_dict(RandomTableValue, classes, 100)

    races = yaml.load(open("tables/race.yml"), Loader=yaml.BaseLoader)
    race_table = RandomTable.from_dict(RandomTableValue, races, 100)

    return background_table, class_table, race_table


BACKGROUND_TABLE, CLASS_TABLE, RACE_TABLE = lambda_init()


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    rolled_stats = CharacterStats.roll_stats()

    character = Character(
        race=RACE_TABLE.choose(),
        background=BACKGROUND_TABLE.choose(),
        character_class=CLASS_TABLE.choose(),
        reroll=CharacterStats.roll_stat(),
        rolled_stats=rolled_stats,
        suggested_stats=None,
    )

    character.suggest_stats()

    character_dict: Dict[str, Any] = {}

    for k, item in character.race.items():
        character_dict[k] = item

    for k, item in character.background.items():
        character_dict[k] = item

    for k, item in character.character_class.items():
        character_dict[k] = item

    character_dict.update({
        "suggested_stats": asdict(character.suggested_stats),
        "rolled_stats": asdict(character.rolled_stats),
        "reroll": character.reroll,
        "attribution": {
            "Random Tables": {
                "author": "Giffyglyph",
                "url": "https://giffyglyph.com/darkerdungeons/",
            },
            "Random Character API": {
                "author": "jworrell",
                "url": "https://github.com/jworrell/darker-dungeons-tools",
            }
        }
    })

    result = json.dumps(character_dict)

    return {
        "statusCode": 200,
        "headers": get_base_headers(len(result)),
        "body": result,
    }


if __name__ == "__main__":
    print(lambda_handler({}, {}))
