from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(    
    name="actiPy",
    version="0.1.2",
    author="Angus Fisk", 
    author_email="angus_fisk@hotmail.com",
    description="Scripts for analysis of actigraphy data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aa-fisk/actigraphy_analysis",
    packages=find_packages(), 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ],
)
