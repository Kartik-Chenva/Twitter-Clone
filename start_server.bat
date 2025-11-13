@echo off
echo ========================================
echo    Twitter Clone - Starting Server
echo ========================================
echo.
echo Navigating to project directory...
cd /d C:\Users\Poonam\Downloads\project

echo.
echo Starting Django development server...
echo.
echo Server will be available at: http://127.0.0.1:8000/
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver

echo.
echo Server stopped.
pause
