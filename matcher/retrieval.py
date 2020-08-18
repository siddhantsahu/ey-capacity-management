"""Implements the retrieval module."""
import functools

import pandas as pd

from dataclasses import Weight
from indexing import build_index
from preprocess import compute_max_values
from skill_match import SkillMatcher


# set constant values or compute from data
MAX_EXPERIENCE, MAX_RANK, MAX_BENCH_AGE = compute_max_values()


def weighted_euclidean_dist(candidate, demand, weight):
    """Compute weighted euclidean distance between normalized demand and candidate vector
    to calculate score.
    
    Args:
        candidate: pd.Series, from candidates_df
        demand: tuple
        weight: tuple
        
    Returns:
        float, distance score between candidate and demand
    """
    dist = 0
    # Note: lower distance score for higher bench age
    dist += (
        weight.technical * (1 - candidate["technical"]) ** 2
        + weight.functional * (1 - candidate["functional"]) ** 2
        + weight.process * (1 - candidate["process"]) ** 2
        + weight.experience
        * (demand.experience / MAX_EXPERIENCE - candidate["years_of_experience"]) ** 2
        + weight.rank * (demand.rank / MAX_RANK - candidate["rank"]) ** 2
        + weight.bench_age ** (1 - candidate["bench_age"]) ** 2
    )
    if demand.location != candidate["location"]:
        dist += weight.location
    return dist ** 0.5


class Retrieval:
    def __init__(self):
        self.index = build_index()
        self.weights = {
            1: Weight(
                technical=0.1,
                functional=0.3,
                process=0.1,
                experience=0.1,
                rank=0.1,
                location=0.3,
                bench_age=0,
            ),
            2: Weight(
                technical=0.1,
                functional=0.25,
                process=0.5,
                experience=0.1,
                rank=0,
                location=0.4,
                bench_age=0.1,
            ),
            3: Weight(
                technical=0.15,
                functional=0.2,
                process=0.05,
                experience=0.2,
                rank=0,
                location=0.1,
                bench_age=0.3,
            ),
        }

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
            technical=lambda x: x["technical"] / 5,
            functional=lambda x: x["functional"] / 5,
            process=lambda x: x["process"] / 5,
            rank=lambda x: x["rank"].str.replace("Rank_", "").astype("int") / MAX_RANK,
            years_of_experience=lambda x: x["years_of_experience"] / MAX_EXPERIENCE,
            bench_age=lambda x: x["bench_age"] / MAX_BENCH_AGE,
        )
        return normalized_df

    def get_results(self, demand, weight_index):
        candidates_df = self.get_candidates_df(demand.skills)
        normalized_df = self.normalize_data(candidates_df)
        normalized_df["distance"] = normalized_df.apply(
            lambda x: weighted_euclidean_dist(x, demand, self.weights[weight_index]), axis=1
        )
        # fitment, i.e. a measure of similarity = 1 / (1+distance)
        normalized_df = normalized_df.assign(fitment=lambda x: 1 / (1 + x["distance"])).drop(
            ["distance", "country", "city"], axis=1
        )
        results = candidates_df.merge(normalized_df[["emp_id", "fitment"]], on="emp_id")
        return results.sort_values("fitment", ascending=False)
