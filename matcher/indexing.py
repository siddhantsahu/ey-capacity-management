"""Indexing module. Builds an index of skills."""
from collections import namedtuple

import pandas as pd
from fuzzywuzzy import fuzz, process
from tabulate import tabulate

from skill_match import SkillMatcher

EmployeeSkillPair = namedtuple("ESPair", ["emp_id", "skill_id", "skill_level"])

# TODO: convert to a class?
def get_emp_skill_pairs(supply_csv, skill_matcher):
    """Generates employee-skill pairs.

    Args:
        supply_csv: str, path to csv file containing supply data
        skill_matcher: SkillMatcher instance

    Returns:
        generator of EmployeeSkillPair
    """
    df = pd.read_csv(supply_csv, sep="\t").fillna("")
    df["skill_concat"] = (
        df[["Sub Unit 1", "Sub Unit 2", "Sub Unit 3", "Skill"]]
        .agg(" ".join, axis=1)
        .str.replace("  ", " ")
    )
    for i, row in df.iterrows():
        skill_name = skill_matcher.match(row["skill_concat"])[0]
        skill_id = skill_matcher.get_idx(skill_name)
        yield EmployeeSkillPair(row["Name/ID"], skill_id, row["Skill Level"])


def spimi(es_pairs):
    """Builds the indexing using SPIMI algorithm.

    Args:
        es_pairs: iterable of EmployeeSkillPair

    Returns:
        dict, index
    """
    index = {}
    for es in es_pairs:
        emp_id, skill_id, skill_level = es
        if skill_id not in index:
            index[skill_id] = {emp_id: skill_level}
        else:
            val = index[skill_id]
            val[emp_id] = skill_level
            index[skill_id] = val
    return index


def main():
    sm = SkillMatcher("../data/skill_tree.csv")
    es_pairs = get_emp_skill_pairs("../data/supply.csv", sm)
    index = spimi(es_pairs)
    return index


if __name__ == "__main__":
    print(main())
