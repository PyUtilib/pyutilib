#
# Create The Following Documents:
#
#   . Managing Python Workflows with pyutilib.workflow
#     workflow.tex
#

all: workflow

workflow: lstanchors
	pdflatex workflow
	bibtex workflow
	pdflatex workflow
	pdflatex workflow

sand: lstanchors
	pdflatex SAND
	bibtex SAND
	pdflatex SAND
	pdflatex SAND

strip_examples:
	python example_exec.py

lstanchors:
	./lstanchors.pl workflow-*.tex

clean:
	@- find . -name '*_strip.py' | xargs rm
	@- find . -name '*.py.bak' | xargs rm
	@- find . -name '*.tex.bak' | xargs rm
