# Simple Makefile for some common tasks. This will get 
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

clean:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r *.egg-info || true
	rm tiddlyweb.log || true
	rm -r store1 || true
	rm -r store2 || true

test: clean
	py.test -x test

dist: test
	python setup.py sdist

upload: clean pypi

pypi: test
	python setup.py sdist upload
