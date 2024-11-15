# makefile 

.PHONY: all
all: format


.PHONY: format
format:
	@echo "Formatting code"
	autopep8 --in-place --aggressive --aggressive --recursive **/*.py


.PHONY: test
test:
	@echo "running tests"
	python -m unittest tests/actogram_plot_tests.py
