# Makefile for RPAL Compiler project

# Set the Python interpreter (change if you're using a different version or virtual environment)
PYTHON = python

# Set the name of the RPAL program file (you can adjust if the file is different)
PROGRAM = myrpal.py

# The default target (when `make` is run without any arguments)
all: run

# Run the RPAL program
run:
	$(PYTHON) $(PROGRAM) $(ARGS)

# Run the tests (you can set up a 'test.py' or test files to run this)
test:
	$(PYTHON) -m unittest discover tests

# Clean up temporary files (remove Python bytecode, etc.)
clean:
	rm -f *.pyc
	rm -rf __pycache__

# Help message (shows available make targets)
help:
	@echo "Makefile for RPAL Compiler"
	@echo "Targets:"
	@echo "  run   - Run the RPAL program"
	@echo "  test  - Run the tests"
	@echo "  clean - Clean up temporary files"
	@echo "  help  - Show this help message"
