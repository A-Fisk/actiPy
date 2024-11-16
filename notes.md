# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### test plot_actogram
- index error, fine passes!
- test subplots passed 
- test different frequency

## TODO
- run on test data 
- Write docstring +/- basic usage 
- update .gitignore 
- switch to venv 
- update/create make file 
- remove bash scripts to create env <- put in makefile
- rename variables to remove animal - put in subject instead 
    - animal_number is \_actogram_plot etc
- move day_label_size to decorator 
- combine waveform into plotting script?
- look through analysis to figure out what want to keep


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

- Actogram
Bunch of different functions to call based on shape of dataframe input
Main plotting function is _actogram_plot

What do we need?
Documentation - better description of what all parameters do, their 
default values and what type of data is expected?

Tidy up code? Refactor see if can be done better?

Look at other functions and figure out what is actually needed


- General
- Write list of all functions in each file

# Resources 

- Example of how to structure repo 
https://github.com/navdeep-G/samplemod/tree/master 


# Scripts 
### Create environment
CONDA_SUBDIR=osx-64 conda env create -f environment.yml

### Update 
CONDA_SUBDIR=osx-64 conda env update -f environment.yml
