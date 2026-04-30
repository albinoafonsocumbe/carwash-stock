@echo off
echo ========================================
echo  Sistema de Gestao de Stock - CarWash
echo ========================================
echo.

set PYTHON=..\venv\Scripts\python.exe
set MANAGE=manage.py

echo [1/3] A verificar dependencias...
..\venv\Scripts\pip install django psycopg2-binary --quiet
echo OK

echo.
echo [2/3] A aplicar migracoes...
%PYTHON% %MANAGE% migrate
if errorlevel 1 (
    echo ERRO: Falha nas migracoes. Verifica se a base de dados existe no PostgreSQL.
    pause
    exit /b 1
)
echo OK

echo.
echo [3/3] A iniciar servidor...
echo.
echo Acede em: http://127.0.0.1:8000
echo Para parar o servidor: CTRL+C
echo.
%PYTHON% %MANAGE% runserver

pause
