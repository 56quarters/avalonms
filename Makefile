#
#

help:
	@echo "Available targets:"
	@echo "    clean: Remove build artifacts"
	@echo "    docs: Build documentation"
	@echo "    init: Set up the development environment"
	@echo "    push: Push origin and github remotes"
	@echo "    test: Run the unit test suite"

clean:
	rm -rf avalonms.egg-info
	cd doc; make clean

doc: site

init:
	python setup.py develop
	pip install -r requires.txt

push:
	git push origin
	git push github

site:
	cd doc; make dirhtml

test:
	ls
