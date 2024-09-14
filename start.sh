#!/bin/bash

PROJECT_ROOT="$(pwd)"

cd "$PROJECT_ROOT" || exit

find "$PROJECT_ROOT" -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/venv/*" -not -path "*/site-packages/*" -delete
find "$PROJECT_ROOT" -path "*/migrations/*.pyc" -not -path "*/venv/*" -not -path "*/site-packages/*" -delete
rm -f "$PROJECT_ROOT/db.sqlite3"

pre-commit install

poetry manage-dev.py makemigrations
poetry manage-dev.py migrate
poetry manage-dev.py runserver

echo "프로젝트 초기화 완료"
