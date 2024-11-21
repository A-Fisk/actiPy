# Plan for actipy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### - calculate interdaily stability
- IS 
- previous notebook in 01_dphil/03_oldgithub

- yeah that's my whole problem with this calculation, have accidentally
done my own version where low is better 

- how have my version vs the other version
- want to do full investigation but that's later 
- for now what do I call my version?
Options 
- IS_fisk
- Easy to access, bit wankery, can change later
- \_calculate_IS 
- also easy to access, suggests less important though
- Something descriptive?
- timepoint_stability?
- since we want low number variation seems good thing to have in title 
- lets try TV - timepoint variability   

- what do I want to test? 
- test with perfect sine wave, should be close to 1 / 0 IS/TV 
- hmmm so what is upper value? - perfectly noisy data? 
- noisy data gives 8.98, does it depend on frequency?
- 10s = 8.98
- h = 8.98 too so doesn't depend
- how about length? that is for 10 days 
- 100 days is 98.9 hmm

- 100 days random noisy data 
- TV 0.9899
- IS 0.01
- TV_h 0.9899
- IS_h 0.01

- 100 days sine wave 
- TV 1.09 e-32
- IS 0.99
- TV_h 1.09 e-32
- IS_h 0.99

- 10 days noise 
- TV 0.89
- IS 0.1
- TV_h 0.898
- IS_h 0.1

- 10 days sine
- TV 1.47 e-33
- IS  0.99
- TV_h 1.47e-33
- IS_h 0.99

- so what edge cases differentiate the results of these two? 
- unstable rhythms check 
- separate project 



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
- test IS/IV catch out invalid value scalar divide (dividing by 0)

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
- write script comparing IS and TV 

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
