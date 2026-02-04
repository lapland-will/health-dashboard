#!/usr/bin/env python3
"""
Oura Ring数据分析器
分析健康数据并生成报告，特别针对自由潜水运动员
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端

class OuraDataAnalyzer:
    """Oura Ring数据分析器"""

    def __init__(self, data_dir=None):
        """
        初始化
        :param data_dir: 数据目录路径
        """
        if data_dir is None:
            data_dir = Path(__file__).parent / "OuraData"
        self.data_dir = Path(data_dir)
        self.report_dir = self.data_dir / "Reports"
        self.report_dir.mkdir(exist_ok=True)

    def load_data(self, file_pattern):
        """加载数据文件"""
        files = list(self.data_dir.glob(file_pattern))
        if not files:
            print(f"未找到匹配的文件: {file_pattern}")
            return None

        # 读取最新的文件
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        print(f"读取文件: {latest_file}")

        if latest_file.suffix == '.json':
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('data', [])
        elif latest_file.suffix == '.csv':
            return pd.read_csv(latest_file)

        return None

    def analyze_sleep_patterns(self):
        """分析睡眠模式"""
        print("\n分析睡眠模式...")

        data = self.load_data("daily_sleep_*.json")
        if not data:
            return

        df = pd.DataFrame(data)

        if df.empty:
            print("没有睡眠数据")
            return

        # 提取关键指标
        metrics = []
        for _, row in df.iterrows():
            if 'score' in row:
                metrics.append({
                    '日期': row.get('day'),
                    '睡眠分数': row['score'].get('overall', 0),
                    '深度睡眠': row['score'].get('deep_sleep', 0),
                    'REM睡眠': row['score'].get('rem', 0),
                    '睡眠效率': row['score'].get('efficiency', 0),
                    '总睡眠时长(小时)': row.get('total_sleep_duration', 0) / 3600,
                    '就寝时间': row.get('bedtime_window', {}).get('start', ''),
                    '起床时间': row.get('bedtime_window', {}).get('end', '')
                })

        if metrics:
            sleep_df = pd.DataFrame(metrics)
            self._save_summary(sleep_df, "sleep_summary")

            # 计算平均值
            avg_sleep_score = sleep_df['睡眠分数'].mean()
            avg_deep_sleep = sleep_df['深度睡眠'].mean()
            avg_rem = sleep_df['REM睡眠'].mean()

            print(f"\n✓ 睡眠分析完成:")
            print(f"  - 平均睡眠分数: {avg_sleep_score:.1f}/100")
            print(f"  - 平均深度睡眠分数: {avg_deep_sleep:.1f}/100")
            print(f"  - 平均REM分数: {avg_rem:.1f}/100")
            print(f"  - 平均睡眠时长: {sleep_df['总睡眠时长(小时)'].mean():.1f}小时")

            return sleep_df

        return None

    def analyze_readiness(self):
        """分析准备度（恢复状态）"""
        print("\n分析身体准备度...")

        data = self.load_data("daily_readiness_*.json")
        if not data:
            return

        df = pd.DataFrame(data)

        if df.empty:
            print("没有准备度数据")
            return

        metrics = []
        for _, row in df.iterrows():
            if 'score' in row:
                metrics.append({
                    '日期': row.get('day'),
                    '准备度分数': row['score'].get('overall', 0),
                    '恢复指数': row['score'].get('recovery_index', 0),
                    '睡眠分数': row['score'].get('sleep', 0),
                    '活动平衡': row['score'].get('activity_balance', 0),
                    'HRV平衡': row['score'].get('hrv_balance', 0),
                    '前一天休息': row['score'].get('resting_hr', 0)
                })

        if metrics:
            readiness_df = pd.DataFrame(metrics)
            self._save_summary(readiness_df, "readiness_summary")

            avg_readiness = readiness_df['准备度分数'].mean()
            avg_recovery = readiness_df['恢复指数'].mean()
            avg_hrv_balance = readiness_df['HRV平衡'].mean()

            print(f"\n✓ 准备度分析完成:")
            print(f"  - 平均准备度分数: {avg_readiness:.1f}/100")
            print(f"  - 平均恢复指数: {avg_recovery:.1f}/100")
            print(f"  - 平均HRV平衡: {avg_hrv_balance:.1f}/100")

            return readiness_df

        return None

    def analyze_activity(self):
        """分析活动数据"""
        print("\n分析活动数据...")

        data = self.load_data("daily_activity_*.json")
        if not data:
            return

        df = pd.DataFrame(data)

        if df.empty:
            print("没有活动数据")
            return

        metrics = []
        for _, row in df.iterrows():
            if 'score' in row:
                metrics.append({
                    '日期': row.get('day'),
                    '活动分数': row['score'].get('overall', 0),
                    '步数': row.get('total_steps', 0),
                    '卡路里(千卡)': row.get('total_calories', 0),
                    '非活动时间(小时)': row.get('inactive_time', 0) / 3600,
                    '中等强度活动(分钟)': row.get('equivalent_walking_distance', 0)
                })

        if metrics:
            activity_df = pd.DataFrame(metrics)
            self._save_summary(activity_df, "activity_summary")

            avg_activity = activity_df['活动分数'].mean()
            avg_steps = activity_df['步数'].mean()

            print(f"\n✓ 活动分析完成:")
            print(f"  - 平均活动分数: {avg_activity:.1f}/100")
            print(f"  - 平均步数: {avg_steps:.0f}")

            return activity_df

        return None

    def analyze_hrv(self):
        """分析心率变异性（对运动员很重要）"""
        print("\n分析心率变异性...")

        data = self.load_data("daily_readiness_*.json")
        if not data:
            return

        # HRV数据通常在准备度数据中
        df = pd.DataFrame(data)

        hrv_data = []
        for _, row in df.iterrows():
            if 'hrv' in row and row['hrv']:
                hrv_data.append({
                    '日期': row.get('day'),
                    '平均HRV': row['hrv'].get('avg_daily_hrv', 0),
                    '最低HRV': row['hrv'].get('lowest_hrv', 0),
                    '夜间HRV': row['hrv'].get('nightly_hrv', 0)
                })

        if hrv_data:
            hrv_df = pd.DataFrame(hrv_data)
            self._save_summary(hrv_df, "hrv_summary")

            avg_hrv = hrv_df['平均HRV'].mean()

            print(f"\n✓ HRV分析完成:")
            print(f"  - 平均每日HRV: {avg_hrv:.1f} ms")
            print(f"  - HRV是训练负荷和恢复的重要指标")

            return hrv_df

        return None

    def _save_summary(self, df, name):
        """保存摘要数据"""
        csv_file = self.report_dir / f"{name}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"  摘要已保存: {csv_file}")

    def generate_weekly_report(self):
        """生成周报"""
        print("\n" + "=" * 60)
        print("生成健康数据周报")
        print("=" * 60)

        # 分析各类数据
        sleep_df = self.analyze_sleep_patterns()
        readiness_df = self.analyze_readiness()
        activity_df = self.analyze_activity()
        hrv_df = self.analyze_hrv()

        # 生成报告文件
        report = []
        report.append("# Oura Ring健康数据周报")
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("\n## 数据摘要\n")

        if readiness_df is not None and not readiness_df.empty:
            latest = readiness_df.iloc[-1]
            report.append("### 身体准备度")
            report.append(f"- 最新准备度分数: {latest['准备度分数']}/100")
            report.append(f"- 平均准备度分数: {readiness_df['准备度分数'].mean():.1f}/100")
            report.append(f"- 趋势: {'↑ 上升' if readiness_df['准备度分数'].tail(7).mean() > readiness_df['准备度分数'].head(7).mean() else '↓ 下降'}")

        if sleep_df is not None and not sleep_df.empty:
            report.append("\n### 睡眠质量")
            report.append(f"- 最新睡眠分数: {sleep_df.iloc[-1]['睡眠分数']}/100")
            report.append(f"- 平均睡眠时长: {sleep_df['总睡眠时长(小时)'].mean():.1f}小时")

        if hrv_df is not None and not hrv_df.empty:
            report.append("\n### 心率变异性 (HRV)")
            report.append(f"- 最新HRV: {hrv_df.iloc[-1]['平均HRV']:.1f} ms")
            report.append(f"- 平均HRV: {hrv_df['平均HRV'].mean():.1f} ms")

        if activity_df is not None and not activity_df.empty:
            report.append("\n### 日常活动")
            report.append(f"- 最新活动分数: {activity_df.iloc[-1]['活动分数']}/100")
            report.append(f"- 平均步数: {activity_df['步数'].mean():.0f}步/天")

        report.append("\n## 自由潜水相关建议\n")

        if readiness_df is not None and not readiness_df.empty:
            latest_readiness = readiness_df.iloc[-1]['准备度分数']
            if latest_readiness >= 85:
                report.append("✓ 身体状态良好，适合高强度训练")
            elif latest_readiness >= 70:
                report.append("⚠ 身体状态一般，建议中等强度训练")
            else:
                report.append("⚠ 身体疲劳，建议休息或轻度训练")

        if hrv_df is not None and not hrv_df.empty:
            latest_hrv = hrv_df.iloc[-1]['平均HRV']
            avg_hrv = hrv_df['平均HRV'].mean()
            if latest_hrv > avg_hrv * 1.1:
                report.append(f"✓ HRV高于平均值({latest_hrv:.1f} ms)，恢复良好")
            elif latest_hrv < avg_hrv * 0.9:
                report.append(f"⚠ HRV低于平均值({latest_hrv:.1f} ms)，可能疲劳累积")

        # 保存报告
        report_file = self.report_dir / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        print(f"\n✓ 周报已生成: {report_file}")

        return '\n'.join(report)

    def export_for_claude(self):
        """导出数据摘要供Claude分析"""
        summary = {
            "生成时间": datetime.now().isoformat(),
            "数据来源": "Oura Ring",
            "分析对象": "金明 - 自由潜水运动员"
        }

        # 收集各类数据摘要
        sleep_df = self.analyze_sleep_patterns()
        readiness_df = self.analyze_readiness()
        activity_df = self.analyze_activity()
        hrv_df = self.analyze_hrv()

        if readiness_df is not None and not readiness_df.empty:
            latest = readiness_df.iloc[-1]
            summary["最新准备度"] = {
                "日期": str(latest['日期']),
                "分数": float(latest['准备度分数']),
                "恢复指数": float(latest['恢复指数']),
                "HRV平衡": float(latest['HRV平衡'])
            }

        if sleep_df is not None and not sleep_df.empty:
            summary["睡眠摘要"] = {
                "平均睡眠时长": float(sleep_df['总睡眠时长(小时)'].mean()),
                "平均睡眠分数": float(sleep_df['睡眠分数'].mean())
            }

        # 保存摘要
        summary_file = self.report_dir / "claude_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Claude数据摘要已生成: {summary_file}")

        return summary


def main():
    """主函数"""
    print("Oura Ring数据分析器")
    print("=" * 60)

    analyzer = OuraDataAnalyzer()

    # 生成周报
    report = analyzer.generate_weekly_report()

    # 导出供Claude使用的数据
    summary = analyzer.export_for_claude()

    print("\n" + "=" * 60)
    print("分析完成！")


if __name__ == "__main__":
    main()
