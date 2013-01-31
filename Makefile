#
#

help:
	@echo "Available targets:"
	@echo "    clean: Remove build artifacts"
	@echo "    doc: Build documentation"
	@echo "    docpreview: Build documentation and start an HTTP server to preview it"
	@echo "    init: Set up the development environment using 'develop' mode (requires root)"
	@echo "    push: Push origin and github remotes"
	@echo "    release: Create and push a new release"
	@echo "    static: Build all static resources (JS, CSS, etc.)"
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
	git push origin
	git push github

release: tags
	python setup.py version
	python setup.py register sdist upload

# NOTE: Order of JS and CSS files matters!
static:
	cat avalon/web/data/js/jquery.js avalon/web/data/js/bootstrap.js avalon/web/data/js/mustache.js > avalon/web/data/js/all.js
	java -jar /opt/yui/current.jar avalon/web/data/js/all.js > avalon/web/data/js/all.min.js
	cat avalon/web/data/css/bootstrap.css avalon/web/data/css/bootstrap-responsive.css avalon/web/data/css/avalon.css > avalon/web/data/css/all.css
	java -jar /opt/yui/current.jar avalon/web/data/css/all.css > avalon/web/data/css/all.min.css

tags: push
	git push --tags origin
	git push --tags github

site:
	cd doc; make dirhtml


