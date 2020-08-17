"""Preprocess module.

- Normalizes supply data by breaking it down into skills list and other metadata -
  experience, location, department etc.
- Computes maximum values of experience, bench age, rank etc that will be used for
  standardization in the retrieval module.
"""
import pandas as pd

from skill_match import SkillMatcher


def normalize_supply():
    """Break supply.csv into skills and metadata information.

    Usage: python normalize_skills.py
    """
    supply = pd.read_csv("../data/supply.csv", sep="\t").fillna("")
    skills_colnames = [
        "Name/ID",
        "Primary Unit",
        "Sub Unit 1",
        "Sub Unit 2",
        "Sub Unit 3",
        "Skill",
        "Skill Level",
    ]
    meta_colnames = [
        "Name/ID",
        "Years of experience",
        "Rank",
        "Service Line",
        "Sub Service Line",
        "SMU",
        "Country",
        "City",
        "Bench Ageing (weeks)",
    ]

    skills = (
        supply[skills_colnames]
        .rename(columns=lambda x: x.lower().replace(" ", "_"))
        .rename(columns={"name/id": "emp_id"})
    )
    meta = (
        (supply[meta_colnames].drop_duplicates().reset_index(drop=True))
        .rename(columns=lambda x: x.lower().replace(" ", "_"))
        .rename(columns={"name/id": "emp_id", "bench_ageing_(weeks)": "bench_age"})
    )

    # note: in a proper database, we would't need this - this for the inconsistencies in the
    # sample data we have, we are mapping the full skill name in supply data to skill tree db
    skills["cat"] = skills[["sub_unit_1", "sub_unit_2", "sub_unit_3", "skill"]].agg(
        " ".join, axis=1
    )
    sm = SkillMatcher("../data/skill_tree.csv")
    skills["skill_id"] = skills["cat"].apply(lambda x: sm.get_idx(sm.match(x)[0]))

    # write the information to disk and use these instead of supply.csv
    meta.to_csv("../data/emp_meta.csv", index=False, sep="\t")
    skills[["emp_id", "skill_id", "skill_level"]].to_csv(
        "../data/emp_skills.csv", sep="\t", index=False
    )


def compute_max_values():
    """Compute maximum values of experience, bench age, rank etc. from meta information.

    In a production scenario, on every insert/update to the employee metadata database,
    compute this and store it to avoid computing on every request. Essentially, this
    function should read the cache and return the value - O(1) lookup.
    """
    meta_df = pd.read_csv("../data/emp_meta.csv", sep="\t")
    max_experience = meta_df["years_of_experience"].max()
    max_rank = meta_df["rank"].str.replace("Rank_", "").astype(int).max()
    max_bench_age = meta_df["bench_age"].max()  # must be in weeks
    return max_experience, max_rank, max_bench_age


if __name__ == "__main__":
    normalize_supply()
