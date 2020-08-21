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

* Create index by running `python indexing.py` inside `matcher` directory.
* Run `python search.py [DEMAND_INDEX] [WEIGHT_INDEX]` to test run search functionality. `DEMAND_INDEX` can be 0-6 and corresponds to the demand in the `demand.csv` file and `WEIGHT_INDEX` 1-3 denotes the weight criteria (hard-coded in file) for service line 1-3.
