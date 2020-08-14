"""Implements the retrieval module."""
import functools
from collections import namedtuple

import pandas as pd

Skills = namedtuple("Skills", ["technical", "functional", "process"])
Demand = namedtuple("Demand", ["skills", "rank", "location", "experience", "bench_age"])


def _get_candidates_for_skills(index, skill_id_list):
    """Get suitable candidates for the requirement.

    Args:
        index: dict, skill index
        skill_id_list: list of skill ids

    Returns:
        dict, {emp_id: skill_level}
    """
    candidates = {}
    for skill_id in skill_id_list:
        if skill_id not in index:
            matches = {}
        else:
            matches = index[skill_id]
        # because of OR operation, we choose the skill with max level
        for k in matches:
            if k in candidates:
                candidates[k] = max(candidates[k], matches[k])
            else:
                candidates[k] = matches[k]
    return candidates


def get_candidates(index, skills):
    """Get all candidates for demanded skills."""
    candidates_with_skills = {
        x: _get_candidates_for_skills(index, skills[x])
        for x in ["technical", "functional", "process"]
    }
    skill_df_list = [
        pd.DataFrame(v.items(), columns=["emp_id", k]) for k, v in candidates_with_skills.items()
    ]

    # merge several dataframes into one - outer join
    # assign 0 as level for skill that does not exist
    skills_df = functools.reduce(
        lambda left, right: pd.merge(left, right, on=["emp"], how="outer"), skill_df_list
    ).fillna(0)
    return skills_df
