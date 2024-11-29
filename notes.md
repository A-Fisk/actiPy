# Plan for circapy

## Overall plans
- Get individual functions working as wanted
- combine files later 

## Current todo 

### Rename whole freaking project!
- circaPy
- actipytools
- actogrampy
- clocklabpy

Places to rename
- pyproject file
- dir name
- imports
- readme
- documentation
- else? 
- github
- remote 


#### README
https://dbader.org/blog/write-a-great-readme-for-your-github-project


#### Documentation 
Tutorial 
https://www.sphinx-doc.org/en/master/tutorial/more-sphinx-customization.html 

## TODO
- publish to pypi
- host sphinx on read-the-docs
- use different template for docs? 
- add in doc urls to pyproject/metadata 
- setup apitoken in twine?
- auto generate wheels and upload - github actions
- add changelog files 

### TODO later/maybe
- Write documentation
- switch to venv 
- move day_label_size to decorator 
- write what expected in docstring parameters 
- detect activity onset 
- gui to select start/end of sleep period? 
- conda env create in makefile?
- Add to pypi
- add in biodare methods 
- check all docstrings in numpy format 
- add to light remap so can remap based on subjective light/dark (half/what
period of day we want) 
- changelog for versions? 
- Activity onset 
- Significance testing of rhythms (chi-square periodogram? how do in actogramJ)
- minimum activity in episodes? 
- add in linux into github actions workflow
- rename lomb_scargle_period to just find period?
- Intel MKL warning on make all? 

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

# changelog
v0.1.5 - updates name to circaPy

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

# Pip
python3 -m build

python3 -m twine upload dist/*

