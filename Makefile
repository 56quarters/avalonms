# Dev shortcuts
#

VIRT_ENV = env

# NOTE: Pretty much all targets are just tasks to run, not steps that actually
# use Make in the cannonical way. The exception is the `env` target that generates
# a virtual  environment
.PHONY : clean
.PHONY : doc
.PHONY : docpreview
.PHONY : push
.PHONY : release
.PHONY : tags
.PHONY : test


help:
	@echo "Available targets:"
	@echo "    clean: Remove build artifacts"
	@echo "    doc: Build documentation"
	@echo "    docpreview: Build documentation and start an HTTP server to preview it"
	@echo "    env: Set up a virtual environment for development"
	@echo "    init: Install dependencies and Avalon in the nested virtual env"
	@echo "    push: Push origin and github remotes"
	@echo "    release: Create and push a new release"
	@echo "    tags: Push newly created tags to origin and github remotes"
	@echo "    test: Run the unit test suite"

clean:
	rm -rf $(VIRT_ENV)
	rm -rf dist
	cd doc; make clean

doc:
	cd doc; make dirhtml

docpreview: doc
	cd doc/_build/dirhtml; $(VIRT_ENV)/bin/python -m SimpleHTTPServer

env:
	virtualenv $(VIRT_ENV)

init: env
	$(VIRT_ENV)/bin/pip install -r requirements.txt --use-mirrors
	$(VIRT_ENV)/bin/pip install -r requirements-test.txt --use-mirrors
	$(VIRT_ENV)/bin/pip install -e .

push:
	git push origin master
	git push github master
	git push bitbucket master

release: tags
	$(VIRT_ENV)/bin/python setup.py version
	$(VIRt_ENV)/bin/python setup.py register sdist upload

tags: push
	git push --tags origin
	git push --tags github
	git push --tags bitbucket

test:
	$(VIRT_ENV)/bin/py.test test
