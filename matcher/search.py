"""Search functionality. Main module."""
from collections import namedtuple

import pandas as pd

from dataclasses import Demand, Dept, Skills
from skill_match import SkillMatcher
from retrieval import Retrieval


def _skill_names_to_ids(names, unit, sm):
    names = list(set([x for x in names if x.strip()]))
    return [sm.get_idx(sm.match(x, unit)[0]) for x in names]


def parse_demand(demand_csv="../data/demand.csv", idx=2):
    demand = pd.read_csv(demand_csv, sep="\t").fillna("")
    demand.columns = [x.strip() for x in demand.columns]

    row = demand.iloc[idx]
    sm = SkillMatcher("../data/skill_tree.csv")

    tech_skill_names = list(set([row[f"Technical Skill {i}"] for i in range(1, 4)]))
    func_skill_names = list(set([row[f"Functional Skill {i}"] for i in range(1, 4)]))
    proc_skill_names = list(set([row[f"Process Skill {i}"] for i in range(1, 4)]))

    tech_skill_ids = _skill_names_to_ids(tech_skill_names, "technical", sm)
    func_skill_ids = _skill_names_to_ids(func_skill_names, "functional", sm)
    proc_skill_ids = _skill_names_to_ids(proc_skill_names, "process", sm)

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


if __name__ == "__main__":
    # TODO: command line parser, weights - by service lines
    demand = parse_demand("../data/demand.csv", 1)
    obj = Retrieval()
    print(obj.get_results(demand))
