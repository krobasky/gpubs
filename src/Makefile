all: 
	python setup.py sdist
	twine upload --repository testpypi dist/*
clean: 
	rm -rf dist/ *.egg-info/ .eggs
