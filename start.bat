@echo off
set PROJECT_ROOT=%cd%

cd %PROJECT_ROOT% || exit /b

:: .py 파일 삭제
for /r %%i in (*.py) do (
    if not "%%~nxi"=="__init__.py" (
        if not "%%i"=="%PROJECT_ROOT%\venv" if not "%%i"=="%PROJECT_ROOT%\site-packages" del "%%i"
    )
)

:: .pyc 파일 삭제
for /r %%i in (*.pyc) do (
    if not "%%i"=="%PROJECT_ROOT%\venv" if not "%%i"=="%PROJECT_ROOT%\site-packages" del "%%i"
)

:: db.sqlite3 삭제
del /f "%PROJECT_ROOT%\db.sqlite3"

:: pre-commit 설치
call pre-commit install

:: 마이그레이션 및 서버 실행
python manage.py makemigrations
python manage.py migrate

echo 프로젝트 초기화 완료
python manage.py runserver
pause
