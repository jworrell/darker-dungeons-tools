import glob
import os
import pickle

import yaml

from darker_dungeons.random_tables import RandomTable


def main():
    for item in glob.glob("tables/*.yml"):
        with open(item) as table_file:
            table = RandomTable.from_dict(yaml.load(table_file, Loader=yaml.BaseLoader))

        filename, _ = os.path.splitext(item)
        tail = os.path.basename(filename)
        pickle_filename = f"pickles/{tail}.pickle"

        with open(pickle_filename, "wb") as pickle_filename:
            pickle.dump(table, pickle_filename)


if __name__ == "__main__":
    main()
