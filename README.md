# EY GDS - Capacity Management using AI

[Hackathon link on Hackerearth](https://www.hackerearth.com/challenges/hackathon/ey-radio-hackathon/)

#### Development environment

Use Python 3.6 and install the following python packages using `conda` (recommended) or `virtualenv`. I used `black` (with line length 100) for formatting python code.
```
pandas
fuzzywuzzy
tabulate
click
black
```

#### Create data files

* `demand.csv` - manually copy relevant data from sample excel file
* `skill_tree.csv`, `supply.csv` - copy corresponding sheets from sample excel file to new csv files
* `emp_meta.csv`, `emp_skills.csv` - after creating the above csv files, run the command `python preprocess.py`

#### Run the program

 Run `python search.py` to test run search functionality. Optionally, for testing different combinations of demands and weights, use `python search.py --demand_index 4 --weight_index 1`

 Demand index refers to the index of the row in `demand.csv` file, `weight_index` 1-3 refers to pre-selected weights for service lines 1-3.