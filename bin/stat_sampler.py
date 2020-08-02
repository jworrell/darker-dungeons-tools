"""
Generate many stat blocks to try to find average stat block
"""

import random


def roll_stat():
    return sum(random.randint(1, 6) for _ in range(3))


def roll_stats():
    stats = [roll_stat() for _ in range(7)]
    return sorted(stats, reverse=True)[:-1]


def main():
    roll_count = 1000000
    stats_sum = [0] * 6

    for _ in range(roll_count):
        stats = roll_stats()

        for i, _ in enumerate(stats_sum):
            stats_sum[i] += stats[i]

    stats_avg = [round(i/roll_count) for i in stats_sum]

    print(stats_sum)
    print(stats_avg)


if __name__ == "__main__":
    main()
