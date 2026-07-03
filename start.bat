@echo off
REM AlgoForge — 一鍵啟動 API + 儀表板（預設 port 8642）
cd /d "%~dp0backend"
if not exist ".venv\Scripts\activate.bat" (
    echo [錯誤] 找不到虛擬環境，請先建立：
    echo     cd backend ^&^& python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)
call ".venv\Scripts\activate.bat"
echo.
echo  AlgoForge 啟動中 — 開瀏覽器到 http://127.0.0.1:8642/
echo  （按 Ctrl+C 停止）
echo.
uvicorn app.main:app --port 8642
