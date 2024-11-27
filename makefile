# makefile 

.PHONY: all
all: format test


.PHONY: format
format:
	@echo "Formatting code"
	autopep8 --in-place --aggressive --aggressive --recursive **/*.py


.PHONY: test
test:
	@echo "running tests"
	python -m unittest tests/preprocessing_tests.py
	python -m unittest tests/activity_tests.py
	python -m unittest tests/periodogram_tests.py
	python -m unittest tests/episode_finder_tests.py
	python -m unittest tests/actogram_plot_tests.py


