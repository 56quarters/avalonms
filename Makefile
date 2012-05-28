#
#

help:
	@echo "Available targets:"
	@echo "    clean: Remove build artifacts"
	@echo "    doc: Build documentation"
	@echo "    docpreview: Build documentation and start an HTTP server to preview it"
	@echo "    init: Set up the development environment"
	@echo "    push: Push origin and github remotes"
	@echo "    test: Run the unit test suite"

clean:
	cd doc; make clean

doc: site

docpreview: doc
	cd doc/_build/dirhtml; python -m SimpleHTTPServer

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
