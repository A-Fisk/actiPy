# makefile 

.PHONY: all
all: format


.PHONY: format
format:
	@echo "Formatting code"
	autopep8 --in-place --aggressive --aggressive --recursive **/*.py
