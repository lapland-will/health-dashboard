#!/bin/bash
###############################################################################
# 金明 - Oura Ring 每日综合健康报告自动发送脚本
# 功能：每天上午11点自动生成并发送全面健康报告看板
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$SCRIPT_DIR/DailyReports"
TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$SCRIPT_DIR/daily_report.log"

# 创建报告目录
mkdir -p "$REPORT_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "开始执行每日综合健康报告生成"
log "=========================================="

cd "$SCRIPT_DIR"

# 运行终极健康看板生成器
log ""
log "步骤1：生成终极健康看板（包含天气、AQI、训练建议）..."
python3 ultimate_dashboard.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "✓ 综合健康看板生成成功"
else
    log "❌ 综合健康看板生成失败"
    exit 1
fi

# 显示报告
REPORT_MD="$REPORT_DIR/dashboard_$TODAY.md"
REPORT_HTML="$REPORT_DIR/dashboard_$TODAY.html"

if [ -f "$REPORT_MD" ]; then
    log ""
    log "=========================================="
    log "今日健康报告"
    log "=========================================="
    cat "$REPORT_MD"
    log ""
    log "=========================================="
    log "报告保存位置:"
    log "  Markdown: $REPORT_MD"
    log "  HTML:     $REPORT_HTML"
    log "=========================================="

    # 在浏览器中打开HTML看板（可选，取消注释以启用）
    # if [[ "$OSTYPE" == "darwin"* ]]; then
    #     open "$REPORT_HTML"
    # fi

    log "✓ 报告已显示"
else
    log "❌ 报告文件未找到: $REPORT_MD"
    exit 1
fi

log ""
log "=========================================="
log "每日综合健康报告任务完成"
log "=========================================="
