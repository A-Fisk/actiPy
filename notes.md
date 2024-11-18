# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### light_phase_activity
- do we want each day? or summary of total? 
- previously have done it just giving us one value for the whole 
data 
- could add in something to generate each day but unless I need it,
why bother? 

- also do we want to add sum/count versions? 
- start with sum because more important 

- what to test? 
- multiple cols/single col? 


## TODO
- light phase activity
- relative amplitude 
- combine waveform into plotting script?
- test mean activity not 24 hours 
- testing normalise activity move baseline/test to setup function/
class attribute 
- write decorator to check if dataframes are empty 
- invert light values actogram so shades dark not light


### TODO later/maybe
- Write documentation
- switch to venv 
- move day_label_size to decorator 
- rename analysis? 
- write what expected in docstring parameters 

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


# Scripts 
### Create environment
CONDA_SUBDIR=osx-64 conda env create -f environment.yml

### Update 
CONDA_SUBDIR=osx-64 conda env update -f environment.yml
