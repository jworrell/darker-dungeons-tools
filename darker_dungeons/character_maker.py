"""
Simple API for rolling new characters
"""

import json
import pickle
from dataclasses import asdict
from typing import Dict, Any

from darker_dungeons.character import CharacterStats, CharacterSheet, roll_3d6, StatRoller, suggest_stats
from darker_dungeons.random_tables import RandomTable, RandomTableValue, RandomClassTableValue, flatten_selections, T, \
    flatten_selections_more, RandomAgeTableValue, RandomDescribedTableValue


def load_table(filename: str) -> RandomTable[T]:
    with open(f"pickles/{filename}.pickle", "rb") as pickle_file:
        return pickle.load(pickle_file)


AGE: RandomTable[RandomAgeTableValue] = load_table("age")
BACKGROUND: RandomTable[RandomTableValue] = load_table("background")
CLASS: RandomTable[RandomClassTableValue] = load_table("class")
FAMILY: RandomTable[RandomTableValue] = load_table("family")
FEATURE: RandomTable[RandomTableValue] = load_table("feature")
HABITS: RandomTable[RandomTableValue] = load_table("habits")
HEIGHT: RandomTable[RandomTableValue] = load_table("height")
MEMORIES: RandomTable[RandomDescribedTableValue] = load_table("memories")
MOTIVATION: RandomTable[RandomDescribedTableValue] = load_table("motivation")
QUEST: RandomTable[RandomDescribedTableValue] = load_table("quest")
RACE: RandomTable[RandomTableValue] = load_table("race")
RAISED_BY: RandomTable[RandomTableValue] = load_table("raised_by")
WEIGHT: RandomTable[RandomTableValue] = load_table("weight")


def get_base_headers(content_length: int) -> Dict[str, str]:
    return {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
        "Content-Length": str(content_length),
    }


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    class_dict = CLASS.choose()
    character_class = flatten_selections(class_dict)

    roller = StatRoller(roll_3d6)
    rolled_stats = CharacterStats.roll_stats(roller)
    reroll = roller.roll_stat()
    suggested_stats = suggest_stats(character_class["preferred_stats"], rolled_stats, reroll)

    character = CharacterSheet(
        race=flatten_selections(RACE.choose()),
        background=flatten_selections(BACKGROUND.choose()),
        character_class=character_class,
        reroll=reroll,
        rolled_stats=rolled_stats,
        suggested_stats=suggested_stats,
    )

    character_dict: Dict[str, Any] = asdict(character)

    age = AGE.choose()

    character_dict["background"].update({
        "family": flatten_selections_more(FAMILY.choose()),
        "memories": sorted(flatten_selections_more(memory) for memory in MEMORIES.choose_many(age["age"].memories)),
        "motivation": flatten_selections_more(MOTIVATION.choose()),
        "habits": flatten_selections_more(HABITS.choose()),
        "quest": flatten_selections_more(QUEST.choose()),
    })

    hp = class_dict["class"].hp

    character_dict.update({
        "max_hp": None if hp is None else int(hp.replace("D", "d").split("d")[1]),
        "gold": class_dict["class"].roll_gold(),
        "equipment": class_dict["class"].choose_equipment(),
    })

    character_dict["appearance"] = {
        "age": flatten_selections_more(age),
        "height": flatten_selections_more(HEIGHT.choose()),
        "weight": flatten_selections_more(WEIGHT.choose()),
        "feature": flatten_selections_more(FEATURE.choose()),
    }

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
