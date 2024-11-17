# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### rewrite mean activity 
- want to take length of n and calculate the mean activity at 
each timepoint 


## TODO
- normalise to baseline
- light phase activity
- relative amplitude 
- combine waveform into plotting script?
- look through analysis to figure out what want to keep
- write test for intradayvariability
- write test for mean_activity
- test mean activity not 24 hours 

### TODO later/maybe
- Write documentation
- switch to venv 
- move day_label_size to decorator 
- rename analysis? 
- write what expected in docstring parameters 

## Questions
- how deal with start time? 
- how deal with missing LDR data? 
- does autopep8 break import order?

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


# Scripts 
### Create environment
CONDA_SUBDIR=osx-64 conda env create -f environment.yml

### Update 
CONDA_SUBDIR=osx-64 conda env update -f environment.yml
