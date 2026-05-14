#!/bin/bash
# CT产业情报Agent - 环境初始化脚本
# 用法: bash setup.sh

set -e

echo "=========================================="
echo "  CT产业情报Agent - 环境初始化"
echo "=========================================="

# 1. 安装Python依赖
echo ""
echo "[1/4] 安装Python依赖..."
pip install -r requirements.txt

# 2. 安装Playwright浏览器
echo ""
echo "[2/4] 安装Playwright浏览器（用于网页采集）..."
playwright install chromium 2>/dev/null || echo "  (Playwright安装可选，跳过)"

# 3. 创建必要目录
echo ""
echo "[3/4] 创建数据目录..."
mkdir -p data/reports
mkdir -p data/plans
mkdir -p knowledge_base

# 4. 配置检查
echo ""
echo "[4/4] 配置检查..."
if [ ! -f .env ]; then
    echo "  ⚠️  未找到 .env 文件，从模板创建..."
    cp .env.example .env
    echo "  📝 请编辑 .env 文件，填入API Key和邮件配置"
else
    echo "  ✅ .env 文件已存在"
fi

echo ""
echo "=========================================="
echo "  初始化完成!"
echo ""
echo "  启动方式:"
echo "    streamlit run web_app.py --server.port 8501"
echo ""
echo "  首次使用请先配置 .env 文件"
echo "=========================================="
