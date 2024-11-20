# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### - calculate interdaily stability
- IS 
- previous notebook in 01_dphil/03_oldgithub

- which version? Published or not? 
- kind of have to have published version

- want to do comparison so kind of want to script both!

- okay done and calculated, but we are getting suuuuper low values for 
perfect sine wave? 
- is this correct?

- not quite right, think I want to take the mean at current data
first? then do the rest? 
- yeah that's my whole problem with this calculation, have accidentally
done my own version where low is better 

## TODO
- update check datetime index decorator - add to non zero values?
- episode finding 
- get travis working again
- update xlabel/ylabel depending on if subplot or not
- rename actogram_plot to just plots 
- add helped for set_circadian_time checking float vs string input 
- rename lomb_scargle_period to just find period?
- move assign_values and generate test data to it's own file? 
- test actogram/get period with T cycles 

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
- add to light remap so can remap based on subjective light/dark (half/what
period of day we want) 

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
