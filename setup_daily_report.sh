#!/bin/bash
###############################################################################
# 金明 - 设置每日上午11点自动发送Oura Ring健康报告
# 使用方法：运行此脚本后，系统会自动配置每天11点的定时任务
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_JOB="0 11 * * * cd $SCRIPT_DIR && ./daily_oura_report.sh >> $SCRIPT_DIR/cron.log 2>&1"

echo "=========================================="
echo "设置每日上午11点自动健康报告"
echo "=========================================="
echo ""

# 检查是否已存在相同的cron任务
if crontab -l 2>/dev/null | grep -q "daily_oura_report.sh"; then
    echo "⚠️  检测到已存在的定时任务"
    echo ""
    echo "当前任务："
    crontab -l 2>/dev/null | grep "daily_oura_report.sh"
    echo ""
    read -p "是否要删除并重新创建？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 删除旧的定时任务
        crontab -l 2>/dev/null | grep -v "daily_oura_report.sh" | crontab -
        echo "✓ 已删除旧任务"
    else
        echo "保留现有任务，退出"
        exit 0
    fi
fi

# 添加新的cron任务
echo "正在添加定时任务..."
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✓ 定时任务设置成功！"
    echo ""
    echo "任务详情："
    echo "  - 执行时间：每天上午 11:00"
    echo "  - 执行脚本：$SCRIPT_DIR/daily_oura_report.sh"
    echo "  - 日志文件：$SCRIPT_DIR/cron.log"
    echo ""
    echo "当前所有定时任务："
    crontab -l
    echo ""
    echo "=========================================="
    echo "✓ 设置完成！"
    echo "=========================================="
    echo ""
    echo "从明天开始，每天上午11点您将收到健康报告"
    echo ""
    echo "如需测试，可立即运行："
    echo "  cd $SCRIPT_DIR"
    echo "  ./daily_oura_report.sh"
    echo ""
else
    echo "❌ 设置失败"
    exit 1
fi
