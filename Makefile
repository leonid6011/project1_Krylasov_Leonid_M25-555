install:
	poetry install

project:
	PYTHONUTF8=1 LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8 poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

lint:
	poetry run ruff check .