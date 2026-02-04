#!/bin/bash
# 启动训练日志系统

cd "$(dirname "$0")"

echo "🚀 启动训练日志系统..."
echo "📝 输入系统: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python3 log_server.py
