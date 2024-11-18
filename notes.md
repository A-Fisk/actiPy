# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### mean wave / activity profile 
- do we want to resample to hourly?

## TODO
- add lights to mean 
- combine waveform into plotting script?
- test mean activity not 24 hours 
- testing normalise activity move baseline/test to setup function/
class attribute 
- write decorator to check if dataframes are empty 
- invert light values actogram so shades dark not light
- add to light remap so can remap based on subjective light/dark (half/what
period of day we want) 
- calculate interdaily stability
- Calculate period 
- update check datetime index decorator - add to non zero values?
- episode finding 
- get travis working again

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
