@echo off
chcp 65001 >nul
echo ====================================
echo Word转PDF服务 - 快速启动
echo ====================================
echo.

echo [1/2] 正在安装依赖...
.venv\Scripts\pip.exe install fastapi uvicorn pydantic python-docx docx2pdf sqlalchemy python-multipart
if errorlevel 1 (
    echo [警告] 部分依赖安装失败，但继续尝试启动...
)

echo.
echo [2/2] 正在启动服务...
echo.
echo ====================================
echo 服务启动后，请访问:
echo   前端界面: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo ====================================
echo.

.venv\Scripts\python.exe main.py
pause
