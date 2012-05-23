#
#

help:
	@echo "Available targets:"
	@echo "    clean: Remove build artifacts"
	@echo "    docs: Build documentation"
	@echo "    push: Push origin and github remotes"
	@echo "    test: Run the unit test suite"

clean:
	rm -rf avalonms.egg-info

docs:
	ls

init:
	python setup.py develop
	pip install -r requires.txt

push:
	git push origin
	git push github

test:
	ls
