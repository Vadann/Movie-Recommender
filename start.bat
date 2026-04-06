@echo off
echo ========================================
echo    Movie Recommender - Quick Start
echo ========================================
echo.

echo Checking if ML model exists...
if not exist "backend\app\ml\movie_data.pkl" (
    echo ML model not found. Running preprocessing...
    cd backend
    call venv\Scripts\activate
    python -m app.ml.preprocessing
    cd ..
    echo.
)

echo Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && python -m app.main"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit this window...
pause >nul

