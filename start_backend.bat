@echo off
echo Starting Samantha backend...
echo Please set your GROQ_API_KEY environment variable first!
echo Example: set GROQ_API_KEY=your_groq_api_key_here
echo.
if "%GROQ_API_KEY%"=="" (
    echo ERROR: GROQ_API_KEY not set! Please set it first.
    pause
    exit /b 1
)
cd backend
python app.py
pause
