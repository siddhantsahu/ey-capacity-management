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
Use `demo.ipynb` jupyter notebook. Setup interactivity in jupyter notebook - [instructions here.](https://towardsdatascience.com/interactive-controls-for-jupyter-notebooks-f5c94829aee6) Or, follow the below instructions if you prefer command line.

Run `python search.py` to test run search functionality. Optionally, for testing different combinations of demands and weights, use `python search.py --demand_index 4 --weight_index 1`

To sort by department, run `python search.py --demand_index 4 --weight_index 1 --sort_by_dept`

Demand index refers to the index of the row in `demand.csv` file, `weight_index` 0-2 refers to the index of the row in `weights.csv` file.