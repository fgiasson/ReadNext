.PHONY: build install-local-build clean test create-venv rebuild-local prepare

build: 
	python3 -m build

install-local-build:
	pip install .

uninstall-local-build:
	pip uninstall -y readnext

rebuild-local:
	nbdev_prepare
	pip uninstall -y readnext
	python3 -m build
	pip install .
	
create-venv:
	python3 -m venv .venv

clean:
	rm -rf dist
	rm -rf chroma_db
	rm -rf docs
	rm -rf recommendations
	rm -rf build
	rm -rf readnext.egg-info
	rm -rf .pytest_cache
	rm -rf tests/__pycache__
	rm -rf readnext/__pycache__
	nbdev_clean --clear_all

# this bundles: nbdev_export, nbdev_test, nbdev_clean and nbdev_readme
# it should be used before pushing to GitHub
prepare:
	nbdev_prepare
