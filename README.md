[![Build Status](https://travis-ci.org/A-Fisk/actigraphy_analysis.png?branch=master)](https://travis-ci.org/A-Fisk/actigraphy_analysis)  


# CircaPy

CircaPy is a python module for circadian analysis of activity data.
It was developed using laboratory
rodents data but is applicable across species and monitoring devices.


## Getting Started

Before you continue you need an installation of Anaconda, available 
[here](https://www.anaconda.com/download).

Then in a terminal of your choice run the following 

```
pip install git+https://github.com/A-Fisk/circaPy.git@main
```

This will install circaPy in your current python environment.
Package dependencies are listed in the environment.yml file 


## Using circaPy

circaPy provides a set of functions to analyse and plot the most common
methods of circadian analysis.

Create some test data 
```
import pandas as pd
import numpy as np
import circaPy.activity as act

# Create a sample dataset with time-series activity data
index = pd.date_range(start='2024-01-01', periods=86400, freq="10s")
values = np.random.randint(0, 100, size=(len(index),2))

df = pd.DataFrame(values, index=index)
``` 

Calculate IV 
```
# Use circaPy's calculate_IV function to compute Interdaily Variability
iv = act.calculate_IV(df)

# Print the result
print(f"Interdaily Variability (IV): {iv:.4f}")
```

Plot actogram 
```
# Use circaPy plot_actogram
import circaPy.actogram_plot as actp

actp.plot_actogram(df, showfig=True)
```



## Contributing 

1. Fork this repository
2. Create branch `git checkout -b <branch-name>
3. Create conda environment
```
conda env create -f environment.yml
conda activate actipy_env
```
4. Make your changes and commit them `git commit -m <commit-message>
    - ensure test suite is passing by running `make all`
5. Push to the original branch `git push origin <project_name>/<location>`
6. Create pull request 


## Authors  

- Angus Fisk 
    - [angus_fisk@hotmail.com](angus_fisk@hotmail.com)
    

## Licence 

- Available under GNU general public licence 




