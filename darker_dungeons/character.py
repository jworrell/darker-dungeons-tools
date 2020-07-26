import random
from dataclasses import dataclass, asdict
from typing import Optional


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
    character_class: CharacterChoice
    reroll: int
    rolled_stats: CharacterStats
    suggested_stats: Optional[CharacterStats]

    def suggest_stats(self):
        rolled_stats = asdict(self.rolled_stats)

        worst_stat = min((v, k) for k, v in rolled_stats.items())

        if worst_stat[0] < self.reroll:
            rolled_stats[worst_stat[1]] = self.reroll

        _ = max((v, k) for k, v in rolled_stats.items())

        self.suggested_stats = CharacterStats(**rolled_stats)
