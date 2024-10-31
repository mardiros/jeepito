package := 'jeepito'
default_test_suite := 'tests'

install:
    uv sync --group dev --group doc

doc:
    cd docs && uv run make html
    xdg-open docs/build/html/index.html

cleandoc:
    cd docs && uv run make clean

gh-pages:
    uv export --group doc -o docs/requirements.txt --no-hashes

gensync:
    uv run python scripts/gen_unasync.py
    uv run ruff format src tests

test: gensync mypy lint unittest

lf:
    uv run pytest -sxvvv --lf

unittest test_suite=default_test_suite:
    uv run pytest -sxv {{test_suite}}

lint:
    uv run ruff check .


fmt:
    uv run ruff check --fix .
    uv run ruff format src tests

black: fmt
    echo "$(tput setaf 3)Warning: Use 'just fmt' instead$(tput setaf 7)"

mypy:
    uv run mypy src/jeepito/ tests/

cov test_suite=default_test_suite:
    rm -f .coverage
    rm -rf htmlcov
    uv run pytest --cov-report=html --cov={{package}} {{test_suite}}
    xdg-open htmlcov/index.html

release major_minor_patch: gensync test gh-pages && changelog
    poetry version {{major_minor_patch}}
    poetry install

changelog:
    uv run python scripts/write_changelog.py
    cat CHANGELOG.rst >> CHANGELOG.rst.new
    rm CHANGELOG.rst
    mv CHANGELOG.rst.new CHANGELOG.rst
    $EDITOR CHANGELOG.rst

publish:
    git commit -am "Release $(poetry version -s --no-ansi)"
    poetry build
    poetry publish
    git push
    git tag "$(poetry version -s --no-ansi)"
    git push origin "$(poetry version -s --no-ansi)"
