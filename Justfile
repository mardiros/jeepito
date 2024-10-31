package := 'jeepito'
default_test_suite := 'tests'

install:
    poetry install

doc:
    cd docs && poetry run make html
    xdg-open docs/build/html/index.html

cleandoc:
    cd docs && poetry run make clean

gh-pages:
    poetry export --with dev -f requirements.txt -o docs/requirements.txt --without-hashes

gensync:
    poetry run python scripts/gen_unasync.py
    poetry run isort src/jeepito/service/_sync/
    poetry run black src/jeepito/service/_sync/
    poetry run isort tests/_sync/
    poetry run black tests/_sync/

test: gensync mypy lint unittest

lf:
    poetry run pytest -sxvvv --lf

unittest test_suite=default_test_suite:
    poetry run pytest -sxv {{test_suite}}

lint:
    poetry run ruff check .


fmt:
    poetry run ruff check --fix .
    poetry run ruff format src tests

black: fmt
    echo "$(tput setaf 3)Warning: Use 'just fmt' instead$(tput setaf 7)"

mypy:
    poetry run mypy src/jeepito/ tests/

cov test_suite=default_test_suite:
    rm -f .coverage
    rm -rf htmlcov
    poetry run pytest --cov-report=html --cov={{package}} {{test_suite}}
    xdg-open htmlcov/index.html

release major_minor_patch: gensync test gh-pages && changelog
    poetry version {{major_minor_patch}}
    poetry install

changelog:
    poetry run python scripts/write_changelog.py
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
