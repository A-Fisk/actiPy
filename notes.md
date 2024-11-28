# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### update xlabel/ylabel depending on if subplot or not

This is an actogram_plot thing isn't it? 
- what is it? 
- params dict plots xlabel and ylabel
- then in plotting_kwargs
- plots using fig.text - so if plotted as part of a subplot, would be 
incorrect
- lets try that in test_dev
- okay yes see problem, now plots for whole fig
how do I update it to work on the subplot ax instead? 
- xlabel easy just do on final ax
- ylabel? 

- okay xlabel worked but overlapping xticks? 
- and yticks also present

- xlabel updated = fine on both single and multiple plots 

- yticks - remove when plotting? 
- update to go with subplot instead of getting subplotspec first? 
- okay that worked for now, will probably break a test or two but for now is
  good
- can then set yticks to be 0
- great, does it also work for xticks? 

## TODO
- update xlabel/ylabel depending on if subplot or not
- rename actogram_plot to just plots 
- add helped for set_circadian_time checking float vs string input 
- rename lomb_scargle_period to just find period?
- move assign_values and generate test data to it's own file? 
- test actogram/get period with T cycles 
- test IS/IV catch out invalid value scalar divide (dividing by 0)

### TODO later/maybe
- Write documentation
- switch to venv 
- move day_label_size to decorator 
- write what expected in docstring parameters 
- detect activity onset 
- gui to select start/end of sleep period? 
- conda env create in makefile?
- Add to pypi
- fix CI - use circle instead? free? 
- add in biodare methods 
- check all docstrings in numpy format 
- add to light remap so can remap based on subjective light/dark (half/what
period of day we want) 
- changelog for versions? 
- Activity onset 
- Significance testing of rhythms (chi-square periodogram? how do in actogramJ)
- minimum activity in episodes? 
- add in linux into github actions workflow

## Questions
- how deal with start time? 
- how deal with missing LDR data? 



# Planning 
## What do we want 

- Actigraphy function
- periodogram functions
    Enright
    Lomb scargle
    ?
- Analysis functions
    - Intra variability
    - Inter stability
        - Old version
        - My version? to be developed 
- Episode detection
- Episode analysis?
    - Mean/Median duration
    - Distribution
- plot mean of time across day


### What do we have
 



### How do we get there
# Resources 

- Example of how to structure repo 
https://github.com/navdeep-G/samplemod/tree/master 
- example of package template
https://github.com/allenai/python-package-template/
- README guide
https://dev.to/scottydocs/how-to-write-a-kickass-readme-5af9

# Scripts 
### Create environment
CONDA_SUBDIR=osx-64 conda env create -f environment.yml

### Update 
CONDA_SUBDIR=osx-64 conda env update -f environment.yml
