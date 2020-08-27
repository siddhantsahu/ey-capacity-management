"""Search functionality. Main module."""
import click
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


def get_weight(weight_csv="../data/weights.csv", idx=1):
    df = pd.read_csv(weight_csv, sep="\t")
    return df.iloc[idx]


@click.command()
@click.option("--demand_index", default=2)
@click.option("--weight_index", default=1)
@click.option("--sort_by_dept", is_flag=True)
def main(demand_index, weight_index, sort_by_dept):
    """Run search.

    Args:
        demand_index: int, 0-6 represents demand (query) from demand.csv
        weight_index: int, 1-3 corresponds to the weight criteria for service line 1-3
    """
    demand = parse_demand("../data/demand.csv", demand_index)
    weight = get_weight("../data/weights.csv", weight_index)
    obj = Retrieval()
    res = obj.get_results(demand, weight, sort_by_dept)
    print(res)


if __name__ == "__main__":
    main()
