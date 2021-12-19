NAME := wolproxypyweb
INSTALL_STAMP := .install.stamp
PRODUCTION_STAMP := .production.stamp
EXPORT_STAMP := .export.stamp
BUILD_STAMP := .build.stamp
POETRY := $(shell command -v poetry 2> /dev/null)
DOCKER := $(shell command -v docker-compose 2> /dev/null)
PRECOMMIT_CONF := .pre-commit-config.yaml

.DEFAULT_GOAL := help

all: format precommit docs install export build docker

.PHONY: help
help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@echo "  install     install packages and prepare the development environment"
	@echo "  production  install packages and prepare the production environment"
	@echo "  build       build dist wheel and tarball files"
	@echo "  export      export all requirements to requirements.txt"
	@echo "  docker      build the docker image"
	@echo "  docs        build documentation via MkDocs"
	@echo "  clean       remove all temporary files"
	@echo "  lint        run the code linters"
	@echo "  format      reformat code"
	@echo "  precommit   run the pre-commit checks on all files"
	@echo "  test        run all the tests"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml poetry.lock
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install --no-root
	$(POETRY) run pre-commit install
	$(POETRY) run pre-commit autoupdate
	touch $(INSTALL_STAMP)

production: $(PRODUCTION_STAMP)
$(PRODUCTION_STAMP): pyproject.toml poetry.lock
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install --no-root --no-dev --no-interaction
	touch $(PRODUCTION_STAMP)

build: $(BUILD_STAMP)
$(BUILD_STAMP): pyproject.toml poetry.lock
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	rm -rf dist/
	$(POETRY) build
	touch $(BUILD_STAMP)

export: $(EXPORT_STAMP)
$(EXPORT_STAMP): pyproject.toml poetry.lock
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) export -f requirements.txt --output requirements.txt --dev --without-hashes
	touch $(EXPORT_STAMP)

docs: $(EXPORT_STAMP)
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) run mkdocs build

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf $(INSTALL_STAMP) $(PRODUCTION_STAMP) .coverage .mypy_cache

.PHONY: lint
lint: $(INSTALL_STAMP)
	$(POETRY) run isort --profile=black --check-only ./tests/ $(NAME)
	$(POETRY) run black --check ./tests/ $(NAME) --diff
	$(POETRY) run flake8 --max-line-length 100 ./tests/ $(NAME)
	$(POETRY) run mypy --ignore-missing-imports ./tests/ $(NAME)
	$(POETRY) run bandit -r $(NAME) -s B608

.PHONY: format
format: $(INSTALL_STAMP)
	$(POETRY) run isort --profile=black ./tests/ $(NAME)
	$(POETRY) run black ./tests/ $(NAME)

.PHONY: precommit
precommit: $(INSTALL_STAMP) $(PRECOMMIT_CONF)
	$(POETRY) run pre-commit run --all-files

.PHONY: test
test: $(INSTALL_STAMP)
	$(POETRY) run pytest ./tests/ --cov-report term-missing --cov-fail-under 100 --cov $(NAME)

.PHONY: docker
docker: $(INSTALL_STAMP)
	@if [ -z $(DOCKER) ]; then echo "Docker could not be found. See https://docs.docker.com/compose/install/"; exit 2; fi
	$(DOCKER) build --force-rm --no-cache
