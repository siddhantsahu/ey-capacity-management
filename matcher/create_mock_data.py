import random

import pandas as pd

from skill_match import SkillMatcher


class SkillGenerator(SkillMatcher):
    def __init__(self, skill_tree_csv):
        super().__init__(skill_tree_csv)
        self.tech_skills = super().get_skill_list(unit="technical")
        self.func_skills = super().get_skill_list(unit="functional")
        self.proc_skills = super().get_skill_list(unit="process")

    def get_random_skill(self, unit="technical"):
        if unit == "technical":
            skill_list = self.tech_skills
        elif unit == "functional":
            skill_list = self.func_skills
        else:
            skill_list = self.proc_skills
        skill_id = super().get_idx(random.choice(skill_list))
        skill_level = random.randint(1, 4)
        return skill_id, skill_level


def mock_emp_meta():
    # taken from EY website
    offices = [
        "Ahmedabad",
        "Bengaluru",
        "Chandigarh",
        "Chennai",
        "Gurgaon",
        "Hyderabad",
        "Jamshedpur",
        "Kochi",
        "Kolkata",
        "Mumbai",
        "New Delhi",
        "Noida",
        "Pune",
    ]
    service_lines = [f"ServiceLine{i}" for i in range(1, 4)]
    sub_service_lines = [f"SubServiceLine{i}" for i in range(1, 5)]
    smus = [f"SMU{i}" for i in range(1, 4)]
    ranks = list(range(6))
    # randomly generate employees
    arr = []
    for i in range(150):
        d = {
            "emp_id": f"Employee {i+14}",
            "years_of_experience": random.randint(0, 30),
            "city": random.choice(offices),
            "country": "India",
            "rank": f"Rank_{random.choice(ranks)}",
            "bench_age": random.randint(1, 12),
            "service_line": random.choice(service_lines),
            "sub_service_line": random.choice(sub_service_lines),
            "smu": random.choice(smus),
        }
        arr.append(d)
    emp_meta_additional = pd.DataFrame(arr)
    return emp_meta_additional


def mock_emp_skills():
    sg = SkillGenerator("../data/skill_tree.csv")
    arr = []
    for i in range(150):
        emp_id = f"Employee {i+14}"
        skills = []
        # tech first
        for tn in range(random.randint(1, 8)):
            sid, slvl = sg.get_random_skill("technical")
            skills.append({"emp_id": emp_id, "skill_id": sid, "skill_level": slvl})
        for fn in range(random.randint(1, 6)):
            sid, slvl = sg.get_random_skill("functional")
            skills.append({"emp_id": emp_id, "skill_id": sid, "skill_level": slvl})
        for pn in range(random.randint(1, 4)):
            sid, slvl = sg.get_random_skill("process")
            skills.append({"emp_id": emp_id, "skill_id": sid, "skill_level": slvl})
        arr += skills
    emp_skills_additional = pd.DataFrame(arr)
    return emp_skills_additional


if __name__ == "__main__":
    emp_meta_mock = mock_emp_meta()
    emp_skills_mock = mock_emp_skills()
    # write to disk
    emp_meta_mock.to_csv("../data/emp_meta_mock.csv", index=False, sep="\t")
    emp_skills_mock.to_csv("../data/emp_skills_mock.csv", index=False, sep="\t")
