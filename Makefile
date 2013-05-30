# Dev shortcuts
#

help:
	@echo "Available targets:"
	@echo "    clean: Remove build artifacts"
	@echo "    doc: Build documentation"
	@echo "    docpreview: Build documentation and start an HTTP server to preview it"
	@echo "    init: Set up the development environment using 'develop' mode (requires root)"
	@echo "    push: Push origin and github remotes"
	@echo "    release: Create and push a new release"
	@echo "    tags: Push newly created tags to origin and github remotes"

clean:
	cd doc; make clean

doc: site

docpreview: doc
	cd doc/_build/dirhtml; python -m SimpleHTTPServer

init:
	python setup.py develop
	pip install -r requires.txt

push:
	git push origin master
	git push github master
	git push bitbucket master

release: tags
	python setup.py version
	python setup.py static register sdist upload

tags: push
	git push --tags origin
	git push --tags github
	git push --tags bitbucket

site:
	cd doc; make dirhtml


