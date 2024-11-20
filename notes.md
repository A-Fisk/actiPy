# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### Calculate period 
- just use lombscargle for now so have something 

- oh something about observation times not being altered for the sampling
  interval? 
- but that shouldn't affect as already doing cycles/observation 
- doing observation times as * sample_freq made it much better 
- Now much better but picking up at 25 hours which is ... weird 

- what if we give it different hour values ?
- okay giving different high periods is affecting results? - shouldn't
high_period = 27 gives at 24.5 hours 
high_period = 30 gives 25 hours for the same data
high_period = 300 gives 70 hours 
- Somthing wrong with the indexing then 
- freq_hours needed adjusting - done 

## TODO
- add to light remap so can remap based on subjective light/dark (half/what
period of day we want) 
- calculate interdaily stability
- update check datetime index decorator - add to non zero values?
- episode finding 
- get travis working again
- update xlabel/ylabel depending on if subplot or not
- rename actogram_plot to just plots 
- add helped for set_circadian_time checking float vs string input 
- rename lomb_scargle_period to just find period?
- move assign_values and generate test data to it's own file? 

### TODO later/maybe
- Write documentation
- switch to venv 
- move day_label_size to decorator 
- rename analysis? 
- write what expected in docstring parameters 
- detect activity onset 
- gui to select start/end of sleep period? 
- conda env create in makefile?
- Add to pypi
- fix CI - use circle instead? free? 
- add in biodare methods 
- check all docstrings in numpy format 

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
