"""Implements the retrieval module."""
import functools
import json

import pandas as pd

from indexing import build_index
from preprocess import compute_max_values
from skill_match import SkillMatcher


# set constant values or compute from data
MAX_EXPERIENCE, MAX_RANK, MAX_BENCH_AGE = compute_max_values()


def candidate_demand_similarity(candidate, demand, weight):
    """Compute weighted euclidean distance between normalized demand and candidate vector
    to calculate similarity score.
    
    Args:
        candidate: pd.Series, from candidates_df
        demand: tuple
        weight: pd.Series
        
    Returns:
        float, distance score between candidate and demand
    """
    dist = 0
    # Note: lower distance score for higher bench age
    dist += (
        weight["technical"] * (1 - candidate["technical"]) ** 2
        + weight["functional"] * (1 - candidate["functional"]) ** 2
        + weight["process"] * (1 - candidate["process"]) ** 2
        + weight["experience"]
        * (demand.experience / MAX_EXPERIENCE - candidate["years_of_experience"]) ** 2
        + weight["rank"] * (demand.rank / MAX_RANK - candidate["rank"]) ** 2
        + weight["bench_age"] ** (1 - candidate["bench_age"]) ** 2
    )
    if demand.location != candidate["location"]:
        dist += weight["location"]
    similarity = 1 / (1 + dist ** 0.5)
    return similarity


def candidate_dept_similarity(candidate, requestor_dept):
    """Similarity between employee's department and requestor department.

    similarity = 3 if both from same service_line+sub_service_line+smu
    similarity = 2 if both from same service_line+sub_service_line
    similarity = 1 if both from same service_line
    similarity = 0 if both from different service_line
    """
    similarity = 0
    if candidate["service_line"].lower() == requestor_dept.service_line.lower():
        similarity += 1
    else:
        return similarity
    if candidate["sub_service_line"].lower() == requestor_dept.sub_service_line.lower():
        similarity += 1
    else:
        return similarity
    if candidate["smu"].lower() == requestor_dept.smu.lower():
        similarity += 1
    return similarity


class Retrieval:
    def __init__(self):
        self.index = build_index()

    def _get_candidates_for_skills(self, skill_id_list):
        """Get suitable candidates for the requirement.

        Args:
            skill_id_list: list of skill ids

        Returns:
            dict, {emp_id: skill_level}
        """
        candidates = {}
        for skill_id in skill_id_list:
            if skill_id not in self.index:
                matches = {}
            else:
                matches = self.index[skill_id]
            # because of OR operation, we choose the skill with max level
            for k in matches:
                if k in candidates:
                    candidates[k] = max(candidates[k], matches[k])
                else:
                    candidates[k] = matches[k]
        return candidates

    def get_candidates_df(self, skills):
        """Get all candidates for demanded skills."""
        candidates_with_skills = {
            "technical": self._get_candidates_for_skills(skills.technical),
            "functional": self._get_candidates_for_skills(skills.functional),
            "process": self._get_candidates_for_skills(skills.process),
        }
        skill_df_list = [
            pd.DataFrame(v.items(), columns=["emp_id", k])
            for k, v in candidates_with_skills.items()
        ]

        # merge several dataframes into one - outer join
        # assign 0 as level for skill that does not exist
        candidates_df = functools.reduce(
            lambda left, right: pd.merge(left, right, on=["emp_id"], how="outer"), skill_df_list
        ).fillna(0)

        # For scalability, only fetch data for the employees in result set
        # should be cached for fast lookup
        meta_df = pd.read_csv("../data/emp_meta.csv", sep="\t")
        candidates_df = candidates_df.merge(meta_df, how="left", on="emp_id")
        return candidates_df

    def normalize_data(self, candidates_df):
        """Normalize candidates dataframe to compute scores."""
        normalized_df = candidates_df.assign(
            location=lambda x: x["city"] + ", " + x["country"],
            technical=lambda x: x["technical"] / 4,
            functional=lambda x: x["functional"] / 4,
            process=lambda x: x["process"] / 4,
            rank=lambda x: x["rank"].str.replace("Rank_", "").astype("int") / MAX_RANK,
            years_of_experience=lambda x: x["years_of_experience"] / MAX_EXPERIENCE,
            bench_age=lambda x: x["bench_age"] / MAX_BENCH_AGE,
        )
        return normalized_df

    def get_results(self, demand, weight, sort_by_dept=False):
        candidates_df = self.get_candidates_df(demand.skills)
        normalized_df = self.normalize_data(candidates_df)
        normalized_df["fitment"] = normalized_df.apply(
            lambda x: candidate_demand_similarity(x, demand, weight), axis=1
        )
        normalized_df["dept_similarity"] = normalized_df.apply(
            lambda x: candidate_dept_similarity(x, demand.dept), axis=1
        )
        normalized_df = normalized_df.drop(["country", "city"], axis=1)
        results = candidates_df.merge(
            normalized_df[["emp_id", "fitment", "dept_similarity"]], on="emp_id"
        )
        if sort_by_dept:
            return results.sort_values(["dept_similarity", "fitment"], ascending=[False, False])
        else:
            return results.sort_values("fitment", ascending=False)
