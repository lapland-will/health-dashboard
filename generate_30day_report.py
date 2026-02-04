#!/usr/bin/env python3
"""
Oura Ring 30天数据综合报告生成器
基于已同步的数据生成完整的30天分析报告
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

def load_oura_data():
    """加载Oura Ring数据"""
    print("=" * 60)
    print("加载Oura Ring 30天数据")
    print("=" * 60)

    # 使用当前目录
    base_dir = Path.cwd()

    # 读取各类数据
    readiness_file = base_dir / "OuraData" / "daily_readiness_2026-01-01_to_2026-01-31.json"
    sleep_file = base_dir / "OuraData" / "daily_sleep_2026-01-01_to_2026-01-31.json"
    activity_file = base_dir / "OuraData" / "daily_activity_2026-01-01_to_2026-01-31.json"

    data = {}

    # 读取准备度数据
    if readiness_file.exists():
        with open(readiness_file, 'r', encoding='utf-8') as f:
            readiness_raw = json.load(f)
            data['readiness'] = readiness_raw.get('data', [])
            print(f"✓ 准备度数据: {len(data['readiness'])}天")

    # 读取睡眠数据
    if sleep_file.exists():
        with open(sleep_file, 'r', encoding='utf-8') as f:
            sleep_raw = json.load(f)
            data['sleep'] = sleep_raw.get('data', [])
            print(f"✓ 睡眠数据: {len(data['sleep'])}天")

    # 读取活动数据
    if activity_file.exists():
        with open(activity_file, 'r', encoding='utf-8') as f:
            activity_raw = json.load(f)
            data['activity'] = activity_raw.get('data', [])
            print(f"✓ 活动数据: {len(data['activity'])}天")

    return data

def analyze_30_days(oura_data):
    """分析30天数据"""
    print("\n" + "=" * 60)
    print("30天趋势分析")
    print("=" * 60)

    # 提取指标
    readiness_scores = []
    sleep_scores = []
    activity_scores = []
    hrv_scores = []
    recovery_scores = []
    dates = []

    if 'readiness' in oura_data:
        for item in oura_data['readiness']:
            dates.append(item.get('day'))
            readiness_scores.append(item.get('score', 0))
            hrv_scores.append(item.get('contributors', {}).get('hrv_balance', 0))
            recovery_scores.append(item.get('contributors', {}).get('recovery_index', 0))

    if 'sleep' in oura_data:
        for item in oura_data['sleep']:
            sleep_scores.append(item.get('score', 0))

    if 'activity' in oura_data:
        for item in oura_data['activity']:
            activity_scores.append(item.get('score', 0))

    # 计算统计数据
    analysis = {
        "天数": len(dates),
        "日期范围": f"{dates[0]} 至 {dates[-1]}" if dates else "无数据",
        "准备度": {
            "平均": sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0,
            "最高": max(readiness_scores) if readiness_scores else 0,
            "最低": min(readiness_scores) if readiness_scores else 0,
            "趋势": "上升" if len(readiness_scores) >= 7 and readiness_scores[-1] > readiness_scores[-7] else "下降" if len(readiness_scores) >= 7 else "平稳"
        },
        "睡眠": {
            "平均": sum(sleep_scores) / len(sleep_scores) if sleep_scores else 0,
            "最高": max(sleep_scores) if sleep_scores else 0,
            "最低": min(sleep_scores) if sleep_scores else 0
        },
        "活动": {
            "平均": sum(activity_scores) / len(activity_scores) if activity_scores else 0,
            "最高": max(activity_scores) if activity_scores else 0,
            "最低": min(activity_scores) if activity_scores else 0
        },
        "HRV平衡": {
            "平均": sum(hrv_scores) / len(hrv_scores) if hrv_scores else 0,
            "最高": max(hrv_scores) if hrv_scores else 0,
            "最低": min(hrv_scores) if hrv_scores else 0
        },
        "恢复指数": {
            "平均": sum(recovery_scores) / len(recovery_scores) if recovery_scores else 0,
            "最高": max(recovery_scores) if recovery_scores else 0,
            "最低": min(recovery_scores) if recovery_scores else 0
        }
    }

    # 打印分析
    print(f"\n数据期间: {analysis['日期范围']}")
    print(f"数据天数: {analysis['天数']}天")

    print(f"\n准备度分数:")
    print(f"  平均: {analysis['准备度']['平均']:.1f}/100")
    print(f"  范围: {analysis['准备度']['最低']}-{analysis['准备度']['最高']}/100")
    print(f"  趋势: {analysis['准备度']['趋势']}")

    print(f"\n睡眠分数:")
    print(f"  平均: {analysis['睡眠']['平均']:.1f}/100")
    print(f"  范围: {analysis['睡眠']['最低']}-{analysis['睡眠']['最高']}/100")

    print(f"\n活动分数:")
    print(f"  平均: {analysis['活动']['平均']:.1f}/100")
    print(f"  范围: {analysis['活动']['最低']}-{analysis['活动']['最高']}/100")

    print(f"\nHRV平衡:")
    print(f"   平均: {analysis['HRV平衡']['平均']:.1f}/100")
    print(f"  范围: {analysis['HRV平衡']['最低']}-{analysis['HRV平衡']['最高']}/100")

    print(f"\n恢复指数:")
    print(f"  平均: {analysis['恢复指数']['平均']:.1f}/100")
    print(f"  范围: {analysis['恢复指数']['最低']}-{analysis['恢复指数']['最高']}/100")

    return analysis, dates, readiness_scores, hrv_scores

def generate_report(oura_data, analysis, dates, readiness_scores, hrv_scores):
    """生成30天综合报告"""
    print("\n" + "=" * 60)
    print("生成30天综合报告")
    print("=" * 60)

    base_dir = Path.cwd()
    report_dir = base_dir / "IntegratedReports"
    report_dir.mkdir(parents=True, exist_ok=True)

    # 创建Markdown报告
    md_content = f"""# 金明 - 30天健康数据综合报告

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**数据期间：** {analysis['日期范围']}
**数据天数：** {analysis['天数']}天
**用户：** 自由潜水世界纪录保持者

---

## 📊 执行摘要

### 整体健康状态

| 指标 | 30天平均 | 范围 | 趋势 | 评价 |
|------|----------|------|------|------|
| **准备度分数** | {analysis['准备度']['平均']:.1f}/100 | {analysis['准备度']['最低']}-{analysis['准备度']['最高']}/100 | {analysis['准备度']['趋势']} | {"⭐ 优秀" if analysis['准备度']['平均'] >= 85 else "✓ 良好" if analysis['准备度']['平均'] >= 70 else "⚠️ 需关注"} |
| **睡眠质量** | {analysis['睡眠']['平均']:.1f}/100 | {analysis['睡眠']['最低']}-{analysis['睡眠']['最高']}/100 | - | {"⭐ 优秀" if analysis['睡眠']['平均'] >= 85 else "✓ 良好"} |
| **活动水平** | {analysis['活动']['平均']:.1f}/100 | {analysis['活动']['最低']}-{analysis['活动']['最高']}/100 | - | {"⭐ 优秀" if analysis['活动']['平均'] >= 85 else "✓ 良好"} |
| **HRV平衡** | {analysis['HRV平衡']['平均']:.1f}/100 | {analysis['HRV平衡']['最低']}-{analysis['HRV平衡']['最高']}/100 | - | {"⭐ 优秀" if analysis['HRV平衡']['平均'] >= 85 else "✓ 良好" if analysis['HRV平衡']['平均'] >= 70 else "⚠️ 需关注"} |
| **恢复指数** | {analysis['恢复指数']['平均']:.1f}/100 | {analysis['恢复指数']['最低']}-{analysis['恢复指数']['最高']}/100 | - | {"✓ 良好" if analysis['恢复指数']['平均'] >= 75 else "⚠️ 略低" if analysis['恢复指数']['平均'] < 70 else "⭐ 优秀"} |

### 自由潜水训练建议

**当前状态评估：**

**准备度：{analysis['准备度']['平均']:.1f}/100** {"✓ 状态优秀，适合高强度训练" if analysis['准备度']['平均'] >= 85 else "✓ 状态良好，适合中等强度训练" if analysis['准备度']['平均'] >= 70 else "⚠️ 状态不佳，建议休息"}

"""

    # 添加训练建议
    avg_readiness = analysis['准备度']['平均']
    avg_hrv = analysis['HRV平衡']['平均']
    avg_recovery = analysis['恢复指数']['平均']

    if avg_readiness >= 85:
        md_content += "- ✓ 可以进行高强度闭气训练\n"
        md_content += "- ✓ 适合深度挑战和极限练习\n"
    elif avg_readiness >= 70:
        md_content += "- ✓ 适合中等强度训练\n"
        md_content += "- ⚠️ 注意监测身体反应\n"
    else:
        md_content += "- ⚠️ 建议休息或轻度训练\n"
        md_content += "- ⚠️ 优先恢复，避免高强度训练\n"

    md_content += f"\n**HRV平衡：{avg_hrv:.1f}/100**\n"
    if avg_hrv >= 85:
        md_content += "- ✓ HRV恢复良好，适合闭气训练\n"
    elif avg_hrv >= 70:
        md_content += "- ✓ HRV可接受，注意训练强度\n"
    else:
        md_content += "- ⚠️ HRV偏低，建议调整训练负荷\n"

    md_content += f"\n**恢复指数：{avg_recovery:.1f}/100**\n"
    if avg_recovery >= 85:
        md_content += "- ✓ 恢复能力优秀\n"
    elif avg_recovery >= 75:
        md_content += "- ✓ 恢复能力良好\n"
    else:
        md_content += "- ⚠️ 恢复能力略低，可能存在疲劳累积\n"

    # 添加最近7天详细数据
    md_content += "\n---\n\n## 📅 最近7天详细数据\n\n"
    md_content += "| 日期 | 准备度 | HRV平衡 | 恢复指数 | 睡眠 | 活动 |\n"
    md_content += "|------|--------|----------|----------|------|------|\n"

    if dates:
        recent_7 = dates[-7:]
        for i in range(len(recent_7)):
            idx = len(dates) - 7 + i
            if 0 <= idx < len(readiness_scores):
                date = recent_7[i]
                readiness = readiness_scores[idx]
                hrv = hrv_scores[idx]
                recovery = recovery_scores[idx]
                md_content += f"| {date} | {readiness} | {hrv} | {recovery} | - | - |\n"

    # 添加趋势分析
    md_content += "\n---\n\n## 📈 趋势分析\n\n"

    # 准备度趋势
    if len(readiness_scores) >= 14:
        first_week_avg = sum(readiness_scores[:7]) / 7
        last_week_avg = sum(readiness_scores[-7:]) / 7
        trend = last_week_avg - first_week_avg

        md_content += "### 准备度变化\n\n"
        md_content += f"- 前7天平均: {first_week_avg:.1f}/100\n"
        md_content += f"- 后7天平均: {last_week_avg:.1f}/100\n"
        md_content += f"- 变化: {trend:+.1f}分 ({'改善' if trend > 0 else '下降' if trend < 0 else '持平'})\n\n"

    # HRV趋势
    if len(hrv_scores) >= 14:
        first_week_hrv = sum(hrv_scores[:7]) / 7
        last_week_hrv = sum(hrv_scores[-7:]) / 7
        hrv_trend = last_week_hrv - first_week_hrv

        md_content += "### HRV平衡变化\n\n"
        md_content += f"- 前7天平均: {first_week_hrv:.1f}/100\n"
        md_content += f"- 后7天平均: {last_week_hrv:.1f}/100\n"
        md_content += f"- 变化: {hrv_trend:+.1f}分 ({'改善' if hrv_trend > 0 else '下降' if hrv_trend < 0 else '持平'})\n\n"

    # 添加华为数据部分
    md_content += "---\n\n## 📱 华为WATCH Ultimate 2 数据\n\n"
    md_content += "**状态：** 设备已连接，数据等待导出\n\n"
    md_content += "### 数据导出步骤：\n\n"
    md_content += "1. **打开华为运动健康App**\n"
    md_content += "2. **选择数据类型导出**\n"
    md_content += "   - 血压数据：健康 → 血压卡片 → 导出CSV\n"
    md_content += "   - 其他数据：我的 → 个人头像 → 请求副本数据\n\n"
    md_content += "3. **保存到指定目录：**\n"
    md_content += "   `Personal/Health/HuaweiData/HealthData/`\n\n"
    md_content += "### 导出后将自动整合到报告中\n\n"

    # 保存报告
    report_file = report_dir / "30_day_comprehensive_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n✓ 报告已生成: {report_file}")
    print(f"✓ 报告目录: {report_dir.absolute()}")

    return report_file

def main():
    """主函数"""
    print("金明 - 30天健康数据综合报告生成器")
    print("=" * 60)

    # 加载数据
    oura_data = load_oura_data()

    if not oura_data.get('readiness'):
        print("\n❌ 未找到Oura Ring数据")
        print("请先运行 oura_ring_sync.py 同步数据")
        return

    # 分析数据
    analysis, dates, readiness_scores, hrv_scores = analyze_30_days(oura_data)

    # 生成报告
    report_file = generate_report(oura_data, analysis, dates, readiness_scores, hrv_scores)

    print("\n" + "=" * 60)
    print("✓ 30天综合报告生成完成！")
    print("=" * 60)
    print(f"\n报告位置: {report_file}")

if __name__ == "__main__":
    main()
