@echo off
REM CT产业情报Agent - Windows环境初始化脚本
REM 用法: 双击运行 或 cmd中执行 setup.bat

echo ==========================================
echo   CT产业情报Agent - 环境初始化
echo ==========================================

echo.
echo [1/4] 安装Python依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，请检查Python环境
    pause
    exit /b 1
)

echo.
echo [2/4] 安装Playwright浏览器（用于网页采集）...
playwright install chromium 2>nul || echo   (Playwright安装可选，跳过)

echo.
echo [3/4] 创建数据目录...
if not exist data\reports mkdir data\reports
if not exist data\plans mkdir data\plans
if not exist knowledge_base mkdir knowledge_base

echo.
echo [4/4] 配置检查...
if not exist .env (
    echo   未找到 .env 文件，从模板创建...
    copy .env.example .env
    echo   请编辑 .env 文件，填入API Key和邮件配置
) else (
    echo   .env 文件已存在
)

echo.
echo ==========================================
echo   初始化完成!
echo.
echo   启动方式:
echo     streamlit run web_app.py --server.port 8501
echo.
echo   首次使用请先配置 .env 文件
echo ==========================================
pause
