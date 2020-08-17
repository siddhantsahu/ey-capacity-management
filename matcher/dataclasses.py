from collections import namedtuple

EmployeeSkillPair = namedtuple("EmployeeSkillPair", ["emp_id", "skill_id", "skill_level"])
Skills = namedtuple("Skills", ["technical", "functional", "process"])
Dept = namedtuple("Department", ["service_line", "sub_service_line", "smu"])
Demand = namedtuple("Demand", ["skills", "rank", "location", "experience", "dept"])
Weight = namedtuple(
    "Weight", ["technical", "functional", "process", "experience", "rank", "location", "bench_age"]
)
