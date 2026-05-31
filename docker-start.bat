@echo off
chcp 65001 >nul
echo ====================================
echo Word转PDF服务 - Docker快速启动
echo ====================================
echo.

:: 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker未安装或未启动
    echo.
    echo 请先安装Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo [OK] Docker已安装
echo.

:: 检查Docker是否运行
docker ps >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker未运行
    echo.
    echo 请启动Docker Desktop
    echo.
    pause
    exit /b 1
)

echo [OK] Docker已运行
echo.

:: 显示菜单
echo 请选择操作:
echo.
echo 1. 构建并启动服务
echo 2. 启动已构建的服务
echo 3. 停止服务
echo 4. 查看日志
echo 5. 重新构建并启动
echo 6. 完全清理
echo 7. 查看服务状态
echo 0. 退出
echo.

set /p choice=请输入选项 (0-7): 

if "%choice%"=="1" goto build_start
if "%choice%"=="2" goto start
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto rebuild
if "%choice%"=="6" goto clean
if "%choice%"=="7" goto status
if "%choice%"=="0" goto end

echo [错误] 无效的选项
goto end

:build_start
echo.
echo [1/3] 正在构建Docker镜像...
docker build -t word2pdf .
if errorlevel 1 (
    echo [错误] 构建失败
    pause
    exit /b 1
)
echo [OK] 镜像构建完成

:start
echo.
echo [2/3] 正在启动服务...
docker-compose up -d
if errorlevel 1 (
    echo [错误] 启动失败
    pause
    exit /b 1
)
echo [OK] 服务已启动

echo.
echo [3/3] 等待服务就绪...
timeout /t 5 /nobreak >nul

echo.
echo ====================================
echo 服务启动成功！
echo ====================================
echo.
echo 前端界面: http://localhost:8000
echo API文档:   http://localhost:8000/docs
echo.
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo.
pause
goto end

:stop
echo.
echo 正在停止服务...
docker-compose down
echo [OK] 服务已停止
echo.
pause
goto end

:logs
echo.
echo 正在打开日志 (按 Ctrl+C 退出)...
docker-compose logs -f
goto end

:rebuild
echo.
echo 正在清理旧容器...
docker-compose down
echo.
echo 正在重新构建镜像...
docker-compose up -d --build
if errorlevel 1 (
    echo [错误] 构建失败
    pause
    exit /b 1
)
echo.
echo [OK] 服务已重新构建并启动
echo.
echo 前端界面: http://localhost:8000
echo.
pause
goto end

:clean
echo.
echo [警告] 将删除所有容器、镜像和数据卷
set /p confirm=确认清理? (y/n): 
if /i not "%confirm%"=="y" goto end

echo.
docker-compose down -v
docker rmi word2pdf 2>nul
echo [OK] 清理完成
echo.
pause
goto end

:status
echo.
docker ps -a --filter "name=word2pdf"
echo.
docker-compose ps
echo.
pause
goto end

:end
