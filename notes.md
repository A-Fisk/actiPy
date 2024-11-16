# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### Rewrite intradayvariability
- what?
- does van someren equation make sense
- does my equation calculate that
- is this what I actually want? 

- old notebook does not have anything on IV
- so if wanted to look at variance of data point to point how would I do that? 

- is fine variance denominator usually n so being in numerator makes sense


## TODO
- intradayvariability
- normalise to baseline
- light phase activity
- relative amplitude 
- maaaybe mean? 
- combine waveform into plotting script?
- look through analysis to figure out what want to keep
- write test for intradayvariability

### TODO later/maybe
- Write documentation
- switch to venv 
- move day_label_size to decorator 
- rename analysis? 

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
