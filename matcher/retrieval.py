"""Implements the retrieval module."""
import functools
from collections import namedtuple
from pdb import set_trace

import pandas as pd

import indexing
from skill_match import SkillMatcher

Skills = namedtuple("Skills", ["technical", "functional", "process"])
Dept = namedtuple("Department", ["service_line", "sub_service_line", "smu"])
Demand = namedtuple("Demand", ["skills", "rank", "location", "experience", "dept"])
Weight = namedtuple(
    "Weight", ["technical", "functional", "process", "experience", "rank", "location", "bench_age"]
)


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


def get_candidates_df(index, skills):
    """Get all candidates for demanded skills."""
    candidates_with_skills = {
        "technical": _get_candidates_for_skills(index, skills.technical),
        "functional": _get_candidates_for_skills(index, skills.functional),
        "process": _get_candidates_for_skills(index, skills.process),
    }
    # set_trace()
    skill_df_list = [
        pd.DataFrame(v.items(), columns=["emp_id", k]) for k, v in candidates_with_skills.items()
    ]

    # merge several dataframes into one - outer join
    # assign 0 as level for skill that does not exist
    candidates_df = functools.reduce(
        lambda left, right: pd.merge(left, right, on=["emp_id"], how="outer"), skill_df_list
    ).fillna(0)
    return candidates_df


def get_supply_metadata(supply_csv):
    supply = pd.read_csv(supply_csv, sep="\t").fillna("")
    meta_info = (
        supply[
            ["Name/ID", "Years of experience", "Rank", "Country", "City", "Bench Ageing (weeks)",]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return meta_info


def normalize_candidates_df(candidates_df, meta_info):
    """Normalize candidates dataframe to compute scores."""
    candidates_df = candidates_df.merge(
        meta_info, how="left", left_on="emp_id", right_on="Name/ID"
    ).drop(["Name/ID"], axis=1)
    max_experience = candidates_df["Years of experience"].max()
    max_bench_age = candidates_df["Bench Ageing (weeks)"].max()

    normalized_df = candidates_df.assign(
        location=lambda x: x["City"] + ", " + x["Country"],
        technical=lambda x: x["technical"] / 5,
        functional=lambda x: x["functional"] / 5,
        process=lambda x: x["process"] / 5,
        rank=lambda x: x["Rank"].str.replace("Rank_", "").astype("int"),
        experience=lambda x: x["Years of experience"] / max_experience,
        bench_age=lambda x: x["Bench Ageing (weeks)"] / max_bench_age,
    ).drop(["Years of experience", "Rank", "Country", "City", "Bench Ageing (weeks)"], axis=1)

    max_rank = normalized_df["rank"].max()
    normalized_df = normalized_df.assign(rank=lambda x: x["rank"] / max_rank)
    return normalized_df, max_experience, max_rank, max_bench_age


def scoring(candidate, demand, weight, max_experience, max_rank, max_bench_age):
    """Compute euclidean distance between normalized demand and candidate vector
    to calculate score.
    
    Args:
        candidate: pd.Series, from candidates_df
        demand: tuple
        weight: tuple
        
    Returns:
        float, distance score between candidate and demand
    """
    s = 0
    s += (
        weight.technical * (1 - candidate["technical"]) ** 2
        + weight.functional * (1 - candidate["functional"]) ** 2
        + weight.process * (1 - candidate["process"]) ** 2
    )
    s += weight.experience * (demand.experience / max_experience - candidate["experience"]) ** 2
    s += weight.rank * (demand.rank / max_rank - candidate["rank"]) ** 2
    if demand.location != candidate["location"]:
        s += weight.location
    s += weight.bench_age ** (1 - candidate["bench_age"]) ** 2
    return s ** 0.5


def skill_names_to_ids(names, unit, sm):
    names = list(set([x for x in names if x.strip()]))
    return [sm.get_idx(sm.match(x, unit)[0]) for x in names]


def parse_demand(demand_csv, idx):
    demand = pd.read_csv(demand_csv, sep="\t").fillna("")
    demand.columns = [x.strip() for x in demand.columns]

    row = demand.iloc[idx]
    sm = SkillMatcher("../data/skill_tree.csv")

    tech_skill_names = [row[f"Technical Skill {i}"] for i in range(1, 4)]
    func_skill_names = [row[f"Functional Skill {i}"] for i in range(1, 4)]
    proc_skill_names = [row[f"Process Skill {i}"] for i in range(1, 4)]

    tech_skill_ids = skill_names_to_ids(tech_skill_names, "technical", sm)
    func_skill_ids = skill_names_to_ids(func_skill_names, "functional", sm)
    proc_skill_ids = skill_names_to_ids(proc_skill_names, "process", sm)

    skills = Skills(tech_skill_ids, func_skill_ids, proc_skill_ids)

    demand = Demand(
        skills,
        int(row["Rank"][-1]),
        "{}, {}".format(row["Location"], row["Country"]),
        row["Min Experience"],
        Dept(
            row["Requestor Service Line"], row["Requestor Sub ServiceLine"], row["Requestor SMU"],
        ),
    )

    return demand


class Retrieval:
    def __init__(self):
        self.index = indexing.main()
        self.meta_info = get_supply_metadata("../data/supply.csv")

    def get_results(self, demand):
        weights = Weight(0.1, 0.3, 0.1, 0.1, 0.1, 0.3, 0)
        candidates_df = get_candidates_df(self.index, demand.skills)
        normalized_df, max_experience, max_rank, max_bench_age = normalize_candidates_df(
            candidates_df, self.meta_info
        )
        distances = []
        for i, row in normalized_df.iterrows():
            dist = scoring(row, demand, weights, max_experience, max_rank, max_bench_age)
            distances.append(dist)
        normalized_df["distance"] = distances
        return normalized_df.sort_values("distance")


if __name__ == "__main__":
    demand = parse_demand("../data/demand.csv", 3)
    obj = Retrieval()
    print(obj.get_results(demand))
