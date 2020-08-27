"""Module to match user typed skill to a skill on our database.

Some ideas to consider:
* Consider abbreviations, e.g. SLA for service level agreement, ML for machine learning etc.
* (Alternatively) Design: Avoid such abnormalities by auto-suggestions while choosing skills
  from a GUI
"""
import pandas as pd
from fuzzywuzzy import fuzz, process
from tabulate import tabulate


def read_skill_tree(csvfile):
    df = pd.read_csv(csvfile, sep="\t").fillna("")
    for c in df:
        df[c] = df[c].str.strip()
    df["skill_name"] = df[["Sub Unit 1", "Sub Unit 2", "Sub Unit 3", "Skill"]].agg(" ".join, axis=1)
    return df


def get_skill_names(df, unit=None):
    assert unit in [
        "Technology",
        "Management",
        "Business Analysis",
        "Finance",
        "Process",
        None,
    ]
    if not unit:
        return df["skill_name"].tolist()
    else:
        return df.loc[df["Sub Unit 1"] == unit, "skill_name"].tolist()


class SkillMatcher:
    def __init__(self, skill_tree_csv):
        self.df = read_skill_tree(skill_tree_csv)
        self.all_skills = get_skill_names(self.df, None)
        self.tech_skills = get_skill_names(self.df, "Technology")
        self.func_skills = (
            get_skill_names(self.df, "Management")
            + get_skill_names(self.df, "Finance")
            + get_skill_names(self.df, "Business Analysis")
        )
        self.proc_skills = get_skill_names(self.df, "Process")

    def get_skill_list(self, unit=None):
        if not unit:
            skills_db = self.all_skills
        elif unit.lower() == "technical":
            skills_db = self.tech_skills
        elif unit.lower() == "functional":
            skills_db = self.func_skills
        elif unit.lower() == "process":
            skills_db = self.proc_skills
        else:
            raise ValueError(
                "Incorrect argument for unit, must be technical or functional or process"
            )
        return skills_db

    def get_idx(self, skill):
        df = self.df
        idx = df.loc[df["skill_name"] == skill, :].index[0]
        return idx

    def match(self, skill, unit=None):
        skills_db = self.get_skill_list(unit)
        return process.extractOne(skill, skills_db, scorer=fuzz.ratio)


if __name__ == "__main__":
    # meant to be run as as standalone script, not as part of a package
    from sys import argv

    obj = SkillMatcher("../data/skill_tree.csv")
    print(obj.match(argv[1], argv[2]))
