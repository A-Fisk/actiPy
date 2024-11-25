# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### Episode finder 

- what do I want ? 
- episodes defined as between 0 and 0
- able to add min_length
- able to add min_activity?

- testing
- test min length and max interruptions
- what do want? 20s min length and 30s max interruption?
- currently not filtering out durations if max interruption allowed 
- problem filtering valid episodes twice, can I fix that? 
- do I need to filter before creating valid episodes the first time?
- or just create episodes 

- how do I test for both? want to get merged episode < min length? 
- subject 2? 
- max_interruptions = 10 merges first two, then min_length 20s gets rid of last
  one 

- getting empty when doing subject 1 min and max, is it just the interruptions
  causing problems? 
- subject 1 is fine 
- okay filtering out is problem, we are getting duration of 20 seconds when
  should be longer, 40 seconds 

- something weird with how handling interruptions 
- going through episodes and checking 

- next check max_interruption logic too 




## TODO
- episode finding 
- move branches around so working on development not testing? 
- move and merge to A-Fisk github 
- get travis working again
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
