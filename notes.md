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

### create test data 

- Current 
- actogram_plot_all_cols
    - goes through each column and calls 
    - actogram_plot_from_df
        - LDR remap
        - prep. Split_entire_df (puts each day in a separate column by given period)
            (have figured this out with EEG LL data?)
            - applies split_dataframe_by_period
            - splits from long to single day per col 
        - \_actogram_plots 


- need to add first and lastr days of 0s 
- one days is very weird and only showing 1 day not 2 
- x axis is also weird and final plot not showing anything 

- why do we have 11 ax with only 10 days?
- how we want it but hmm 



- how deal with start time? 
- how deal with missing LDR data? 


## TODO
- run on test data 
- Write docstring +/- basic usage 
- update .gitignore 
- switch to venv 
- update/create make file 
- remove bash scripts to create env <- put in makefile
- rename variables to remove animal - put in subject instead 
    - animal_number is \_actogram_plot etc
- remove subplot kwarg from \_actogram_plot
- move day_label_size to decorator 

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
