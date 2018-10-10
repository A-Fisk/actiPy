import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="actigraphyanalysis",
    version="0.0.1",
    author="Angus Fisk", 
    author_email="angus_fisk@hotmail.com",
    description="Scripts for analysis of actigraphy data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/A-Fisk/actigraphy_analysis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ],
)
