# Plan for actipy

## Next steps/notes
- how to develop?
- what environment to use?
    - have currently specified packages in env.yml file but not great 
    for ongoing use ?    
    - if anything don't want environment? - no definitely do,
    and maintain version numbers but that's an ongoing maintenance problem
- okay so create + activate env 
- actually switch to venv because easier/wider us
- Do I want a class or just a bunch of functions?
    - Useful when want to glue state and functionality
    - But can be confusing and make things less clear.
    - Don't really need to, so won't! 
    - hitchhikers guide to python
- Need test data  
- need tests!
- so how to develop - in dir or in separate dir?
- lets do it all in dir - py file to create test_data, put in 
- just do in test dir, and use to run tests?  

### update environment 
- for now stick with conda 
- take from LL-
- okay done but don't know if it has broken everything 

## TODO
- Update environment 
- update version number 
- Create test data 
- run on test data 
- Write docstring +/- basic usage 
- update .gitignore 
- switch to venv 

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


# Scripts 
### Create environment
CONDA_SUBDIR=osx-64 conda env create -f environment.yml

### Update 
CONDA_SUBDIR=osx-64 conda env update -f environment.yml
