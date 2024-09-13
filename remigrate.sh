#!/bin/bash

PROJECT_ROOT="/Users/iih/PycharmProjects/blogAPI"

cd "$PROJECT_ROOT" || exit
source "$PROJECT_ROOT/.venv/bin/activate"

find "$PROJECT_ROOT" -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/venv/*" -not -path "*/site-packages/*" -delete
find "$PROJECT_ROOT" -path "*/migrations/*.pyc" -not -path "*/venv/*" -not -path "*/site-packages/*" -delete
rm -f "$PROJECT_ROOT/db.sqlite3"

python manage-dev.py makemigrations
python manage-dev.py migrate
python manage-dev.py search_index --rebuild
python manage-dev.py runserver

echo "마이그레이션 초기화 완료"