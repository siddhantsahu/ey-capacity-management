"""Indexing module. Builds an index of skills."""
from collections import namedtuple

import pandas as pd
from fuzzywuzzy import fuzz, process
from tabulate import tabulate

from skill_match import SkillMatcher


EmployeeSkillPair = namedtuple("EmployeeSkillPair", ["emp_id", "skill_id"])


def get_emp_skill_pairs(emp_skills_csv):
    """Generates employee-skill pairs. The ingestion part could be easily changed
    to connect to a database instead of reading from a csv file.

    Args:
        emp_skills_csv: str, path to file containing skills data for employees

    Returns:
        generator of tuples
    """
    df = pd.read_csv(emp_skills_csv, sep="\t")
    for row in df.itertuples():
        es_pair = EmployeeSkillPair(row.emp_id, row.skill_id)
        yield es_pair


def spimi(es_pairs):
    """Builds the indexing using SPIMI algorithm.

    Args:
        es_pairs: iterable of tuples with employee skill pairs

    Returns:
        dict, index
    """
    index = {}
    for es in es_pairs:
        emp_id, skill_id = es
        if skill_id not in index:
            index[skill_id] = [emp_id]
        else:
            postings_list = index[skill_id]
            postings_list.append(emp_id)
            index[skill_id] = postings_list
    return index


def build_index():
    es_pairs = get_emp_skill_pairs("../data/emp_skills.csv")
    index = spimi(es_pairs)
    return index


if __name__ == "__main__":
    index = build_index()
    from pprint import pprint

    pprint(index)
