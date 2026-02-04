#!/usr/bin/env python3
"""
增强可视化模块 - 生成7天、30天趋势图表
包括饮食、训练、睡眠、HRV等多维度可视化
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path
import json


class EnhancedVisualizer:
    """增强可视化器 - 生成更多图表"""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.charts_dir = self.output_dir / "charts"
        self.charts_dir.mkdir(exist_ok=True)
        self.data_dir = self.output_dir / "historical_data"
        self.data_dir.mkdir(exist_ok=True)

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

    def generate_mock_historical_data(self, days=30):
        """生成模拟历史数据（用于演示）"""
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(days-1, -1, -1)]

        # 生成带趋势的模拟数据
        import random
        random.seed(42)

        data = {
            "dates": [d.strftime("%Y-%m-%d") for d in dates],
            "readiness": [],
            "sleep_score": [],
            "hrv_balance": [],
            "recovery_index": [],
            "resting_hr": [],
            "sleep_balance": [],
            "activity_balance": [],
            "deep_sleep": [],
            "rem_sleep": [],
            "sleep_efficiency": [],
            "training_intensity": [],
            "calories_intake": []
        }

        base_readiness = 75
        base_sleep = 70
        base_hrv = 70

        for i in range(days):
            # 添加波动和趋势
            readiness = base_readiness + (i * 0.3) + random.uniform(-8, 8)
            sleep = base_sleep + (i * 0.2) + random.uniform(-10, 10)
            hrv = base_hrv + (i * 0.4) + random.uniform(-12, 12)

            readiness = max(50, min(100, readiness))
            sleep = max(50, min(100, sleep))
            hrv = max(40, min(100, hrv))

            data["readiness"].append(int(readiness))
            data["sleep_score"].append(int(sleep))
            data["hrv_balance"].append(int(hrv))
            data["recovery_index"].append(int(min(100, max(60, hrv + random.uniform(-5, 5)))))
            data["resting_hr"].append(int(min(100, max(70, 90 - (readiness-70)*0.3))))
            data["sleep_balance"].append(int(min(100, max(60, sleep + random.uniform(-5, 5)))))
            data["activity_balance"].append(int(min(100, max(60, 75 + random.uniform(-10, 10)))))
            data["deep_sleep"].append(int(min(100, max(50, sleep * 0.95 + random.uniform(-5, 5)))))
            data["rem_sleep"].append(int(min(100, max(50, sleep * 0.98 + random.uniform(-5, 5)))))
            data["sleep_efficiency"].append(int(min(100, max(80, 92 + random.uniform(-5, 5)))))

            # 训练强度（0-3：休息、低、中、高）
            intensity = random.choices([0, 1, 2, 3], weights=[10, 20, 40, 30])[0]
            data["training_intensity"].append(intensity)

            # 热量摄入
            if intensity == 3:
                calories = 3000
            elif intensity == 2:
                calories = 2600
            else:
                calories = 2200
            data["calories_intake"].append(calories)

        return data

    def create_30_day_trend_chart(self, data):
        """生成30天趋势图"""
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle('30天健康趋势分析', fontsize=16, fontweight='bold', y=0.995)

        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]

        # 子图1：准备度和睡眠
        ax1 = axes[0]
        ax1.plot(dates, data["readiness"], label='准备度', marker='o', linewidth=2, markersize=4, color='#667eea')
        ax1.plot(dates, data["sleep_score"], label='睡眠分数', marker='s', linewidth=2, markersize=4, color='#8b5cf6')
        ax1.fill_between(dates, data["readiness"], alpha=0.3, color='#667eea')
        ax1.fill_between(dates, data["sleep_score"], alpha=0.3, color='#8b5cf6')
        ax1.set_ylabel('分数', fontsize=11, fontweight='bold')
        ax1.set_title('准备度 & 睡眠分数趋势（30天）', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper left', framealpha=0.9)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(50, 100)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        # 子图2：HRV和恢复指数
        ax2 = axes[1]
        ax2.plot(dates, data["hrv_balance"], label='HRV平衡', marker='o', linewidth=2, markersize=4, color='#10b981')
        ax2.plot(dates, data["recovery_index"], label='恢复指数', marker='s', linewidth=2, markersize=4, color='#059669')
        ax2.fill_between(dates, data["hrv_balance"], alpha=0.3, color='#10b981')
        ax2.set_ylabel('分数', fontsize=11, fontweight='bold')
        ax2.set_title('HRV平衡 & 恢复指数趋势（30天）', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper left', framealpha=0.9)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(40, 100)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        # 子图3：训练强度
        ax3 = axes[2]
        intensity_labels = {0: '休息', 1: '低', 2: '中', 3: '高'}
        intensity_colors = {0: '#9ca3af', 1: '#fbbf24', 2: '#3b82f6', 3: '#ef4444'}

        for i in range(len(dates)-1):
            intensity = data["training_intensity"][i]
            color = intensity_colors[intensity]
            ax3.bar(dates[i], 1, width=timedelta(days=0.8), color=color, alpha=0.7, edgecolor='white', linewidth=0.5)

        ax3.set_ylabel('训练强度', fontsize=11, fontweight='bold')
        ax3.set_title('训练强度分布（30天）', fontsize=12, fontweight='bold')
        ax3.set_ylim(0, 1.2)
        ax3.set_yticks([])

        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=label, alpha=0.7)
                          for label, color in [('休息', '#9ca3af'), ('低强度', '#fbbf24'),
                                              ('中强度', '#3b82f6'), ('高强度', '#ef4444')]]
        ax3.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        plt.tight_layout()

        output_file = self.charts_dir / "30_day_trends.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return output_file

    def create_sleep_quality_distribution(self, data):
        """生成睡眠质量分布图"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('睡眠质量深度分析（30天）', fontsize=16, fontweight='bold', y=0.98)

        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]

        # 1. 深睡和REM趋势
        ax = axes[0, 0]
        ax.plot(dates, data["deep_sleep"], label='深睡质量', marker='o', linewidth=2, markersize=3, color='#8b5cf6')
        ax.plot(dates, data["rem_sleep"], label='REM质量', marker='s', linewidth=2, markersize=3, color='#6366f1')
        ax.set_title('深睡 & REM 趋势', fontsize=11, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(50, 100)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        # 2. 睡眠效率
        ax = axes[0, 1]
        ax.plot(dates, data["sleep_efficiency"], color='#10b981', linewidth=2, marker='o', markersize=3)
        ax.fill_between(dates, data["sleep_efficiency"], alpha=0.3, color='#10b981')
        ax.set_title('睡眠效率趋势', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(80, 100)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        # 3. 睡眠平衡分布
        ax = axes[1, 0]
        ax.hist(data["sleep_balance"], bins=15, color='#8b5cf6', alpha=0.7, edgecolor='white')
        ax.axvline(sum(data["sleep_balance"])/len(data["sleep_balance"]), color='red', linestyle='--', linewidth=2, label='平均')
        ax.set_title('睡眠平衡分布', fontsize=11, fontweight='bold')
        ax.set_xlabel('睡眠平衡分数')
        ax.set_ylabel('天数')
        ax.legend()

        # 4. 睡眠质量雷达（最近7天 vs 30天平均）
        ax = axes[1, 1]
        categories = ['总睡眠', '深睡', 'REM', '效率', '规律']
        recent_7 = [
            sum(data["sleep_score"][-7:])//7,
            sum(data["deep_sleep"][-7:])//7,
            sum(data["rem_sleep"][-7:])//7,
            sum(data["sleep_efficiency"][-7:])//7,
            sum(data["sleep_balance"][-7:])//7
        ]
        avg_30 = [
            sum(data["sleep_score"])//len(data["sleep_score"]),
            sum(data["deep_sleep"])//len(data["deep_sleep"]),
            sum(data["rem_sleep"])//len(data["rem_sleep"]),
            sum(data["sleep_efficiency"])//len(data["sleep_efficiency"]),
            sum(data["sleep_balance"])//len(data["sleep_balance"])
        ]

        angles = [n / len(categories) * 2 * 3.14159 for n in range(len(categories))]
        angles += angles[:1]

        recent_7 += recent_7[:1]
        avg_30 += avg_30[:1]

        ax = plt.subplot(2, 2, 4, projection='polar')
        ax.plot(angles, recent_7, 'o-', linewidth=2, label='最近7天', color='#667eea')
        ax.fill(angles, recent_7, alpha=0.25, color='#667eea')
        ax.plot(angles, avg_30, 'o-', linewidth=2, label='30天平均', color='#8b5cf6')
        ax.fill(angles, avg_30, alpha=0.25, color='#8b5cf6')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=9)
        ax.set_ylim(50, 100)
        ax.set_title('睡眠质量对比', fontsize=11, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)

        plt.tight_layout()

        output_file = self.charts_dir / "sleep_quality_distribution.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return output_file

    def create_nutrition_visualization(self, data):
        """生成营养摄入可视化"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('营养摄入分析（30天）', fontsize=16, fontweight='bold', y=0.98)

        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]

        # 1. 热量摄入趋势
        ax = axes[0, 0]
        ax.plot(dates, data["calories_intake"], marker='o', linewidth=2, markersize=4, color='#f59e0b')
        ax.fill_between(dates, data["calories_intake"], alpha=0.3, color='#f59e0b')
        ax.set_title('每日热量摄入', fontsize=11, fontweight='bold')
        ax.set_ylabel('热量 (kcal)')
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        # 添加训练强度背景色
        for i in range(len(dates)):
            intensity = data["training_intensity"][i]
            if intensity == 3:
                ax.axvspan(dates[i]-timedelta(hours=12), dates[i]+timedelta(hours=12),
                          alpha=0.1, color='red', label='高强度' if i == len(dates)-1 else "")

        # 2. 热量摄入分布
        ax = axes[0, 1]
        calories_dist = {2200: 0, 2600: 0, 3000: 0}
        for c in data["calories_intake"]:
            calories_dist[c] += 1

        colors = ['#10b981', '#3b82f6', '#ef4444']
        labels = ['恢复日\n2200kcal', '中等强度\n2600kcal', '高强度\n3000kcal']
        values = [calories_dist[2200], calories_dist[2600], calories_dist[3000]]

        wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%',
                                           startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax.set_title('热量摄入分布（30天）', fontsize=11, fontweight='bold')

        # 3. 营养比例饼图（两餐制）
        ax = axes[1, 0]
        sizes = [30, 35, 35]  # 蛋白质、脂肪、碳水
        labels = ['蛋白质\n30%', '脂肪\n35%', '碳水\n35%']
        colors = ['#667eea', '#f59e0b', '#10b981']
        explode = (0.05, 0.05, 0.05)

        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                           autopct='%1.1f%%', startangle=90,
                                           textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax.set_title('营养素比例', fontsize=11, fontweight='bold')

        # 4. 第一餐 vs 第二餐热量分配
        ax = axes[1, 1]
        meals = ['第一餐\n(午餐)\n45%', '第二餐\n(晚餐)\n40%', '训练前\n加餐\n5%', '其他\n10%']
        sizes = [45, 40, 5, 10]
        colors = ['#667eea', '#764ba2', '#10b981', '#f59e0b']

        wedges, texts, autotexts = ax.pie(sizes, labels=meals, colors=colors, autopct='%1.1f%%',
                                           startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax.set_title('热量分配（两餐制）', fontsize=11, fontweight='bold')

        plt.tight_layout()

        output_file = self.charts_dir / "nutrition_visualization.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return output_file

    def create_training_calendar(self, data):
        """生成训练日历热图"""
        fig, ax = plt.subplots(figsize=(14, 6))

        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]

        # 创建热图数据
        intensity_matrix = []
        week_data = []

        for i, date in enumerate(dates):
            intensity = data["training_intensity"][i]
            week_data.append(intensity)

            if date.weekday() == 6 or i == len(dates) - 1:  # 周日或最后一天
                intensity_matrix.append(week_data)
                week_data = []

        # 绘制热图
        im = ax.imshow(intensity_matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=3)

        # 设置刻度
        ax.set_xticks(range(7))
        ax.set_xticklabels(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
        ax.set_yticks(range(len(intensity_matrix)))

        # 添加周标签
        week_labels = []
        for i in range(len(intensity_matrix)):
            week_num = i + 1
            week_labels.append(f'第{week_num}周')
        ax.set_yticklabels(week_labels, fontsize=9)

        # 在每个格子中显示强度
        for i in range(len(intensity_matrix)):
            for j in range(len(intensity_matrix[i])):
                intensity = intensity_matrix[i][j]
                text = ax.text(j, i, ['', '低', '中', '高'][intensity],
                             ha="center", va="center", color="white", fontweight='bold')

        ax.set_title('训练日历（30天）', fontsize=14, fontweight='bold', pad=15)

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.1, fraction=0.05)
        cbar.set_ticks([0.375, 1.125, 1.875, 2.625])
        cbar.set_ticklabels(['休息', '低强度', '中强度', '高强度'])

        plt.tight_layout()

        output_file = self.charts_dir / "training_calendar.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return output_file

    def create_readiness_comprehensive(self, data):
        """生成准备度综合分析图"""
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        fig.suptitle('准备度综合分析（30天）', fontsize=16, fontweight='bold', y=0.98)

        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]

        # 1. 准备度趋势（上）
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(dates, data["readiness"], marker='o', linewidth=2.5, markersize=4, color='#667eea', label='准备度')
        ax1.fill_between(dates, data["readiness"], alpha=0.3, color='#667eea')

        # 添加平均水平线
        avg_readiness = sum(data["readiness"]) / len(data["readiness"])
        ax1.axhline(y=avg_readiness, color='red', linestyle='--', linewidth=2, label=f'平均: {avg_readiness:.1f}')
        ax1.axhline(y=85, color='green', linestyle=':', linewidth=1.5, alpha=0.7, label='最佳状态线')

        ax1.set_title('准备度趋势', fontsize=12, fontweight='bold')
        ax1.set_ylabel('分数', fontsize=11, fontweight='bold')
        ax1.legend(loc='upper left', framealpha=0.9)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(50, 100)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        # 2. 各指标分布（左中）
        ax2 = fig.add_subplot(gs[1, 0])
        metrics = ['HRV平衡', '恢复指数', '静息心率', '睡眠平衡', '活动平衡']
        box_data = [
            data["hrv_balance"],
            data["recovery_index"],
            data["resting_hr"],
            data["sleep_balance"],
            data["activity_balance"]
        ]

        bp = ax2.boxplot(box_data, labels=metrics, patch_artist=True, medianprops=dict(color='red', linewidth=2))
        for patch, color in zip(bp['boxes'], ['#667eea', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        ax2.set_title('各指标分布（箱线图）', fontsize=11, fontweight='bold')
        ax2.set_ylabel('分数', fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # 3. 准备度分布直方图（右中）
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.hist(data["readiness"], bins=15, color='#667eea', alpha=0.7, edgecolor='white')
        ax3.axvline(avg_readiness, color='red', linestyle='--', linewidth=2, label=f'平均: {avg_readiness:.1f}')
        ax3.axvline(85, color='green', linestyle=':', linewidth=2, label='最佳线')
        ax3.set_title('准备度分布', fontsize=11, fontweight='bold')
        ax3.set_xlabel('准备度分数')
        ax3.set_ylabel('天数')
        ax3.legend()

        # 4. 各指标相关性热图（下）
        ax4 = fig.add_subplot(gs[2, :])

        # 计算相关系数
        import numpy as np
        correlations = np.corrcoef([
            data["readiness"],
            data["hrv_balance"],
            data["recovery_index"],
            data["sleep_score"],
            data["activity_balance"]
        ])

        im = ax4.imshow(correlations, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

        ax4.set_xticks(range(5))
        ax4.set_yticks(range(5))
        ax4.set_xticklabels(['准备度', 'HRV', '恢复', '睡眠', '活动'], fontsize=10)
        ax4.set_yticklabels(['准备度', 'HRV', '恢复', '睡眠', '活动'], fontsize=10)

        # 添加相关系数标注
        for i in range(5):
            for j in range(5):
                text = ax4.text(j, i, f'{correlations[i, j]:.2f}',
                              ha="center", va="center", color="black", fontweight='bold')

        ax4.set_title('指标相关性热图', fontsize=11, fontweight='bold')

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax4, orientation='horizontal', pad=0.15, fraction=0.05)
        cbar.set_label('相关系数', fontsize=10)

        plt.tight_layout()

        output_file = self.charts_dir / "readiness_comprehensive.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return output_file

    def generate_all_charts(self):
        """生成所有增强图表"""
        print("📊 生成增强可视化图表...")

        # 生成或加载历史数据
        data_file = self.data_dir / "historical_data.json"

        if data_file.exists():
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            data = self.generate_mock_historical_data(days=30)
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)

        # 生成各种图表
        charts = []

        try:
            chart1 = self.create_30_day_trend_chart(data)
            charts.append(("30天趋势图", chart1))
            print(f"  ✓ {chart1}")
        except Exception as e:
            print(f"  ⚠️ 30天趋势图生成失败: {e}")

        try:
            chart2 = self.create_sleep_quality_distribution(data)
            charts.append(("睡眠质量分布", chart2))
            print(f"  ✓ {chart2}")
        except Exception as e:
            print(f"  ⚠️ 睡眠质量分布生成失败: {e}")

        try:
            chart3 = self.create_nutrition_visualization(data)
            charts.append(("营养摄入分析", chart3))
            print(f"  ✓ {chart3}")
        except Exception as e:
            print(f"  ⚠️ 营养摄入分析生成失败: {e}")

        try:
            chart4 = self.create_training_calendar(data)
            charts.append(("训练日历", chart4))
            print(f"  ✓ {chart4}")
        except Exception as e:
            print(f"  ⚠️ 训练日历生成失败: {e}")

        try:
            chart5 = self.create_readiness_comprehensive(data)
            charts.append(("准备度综合分析", chart5))
            print(f"  ✓ {chart5}")
        except Exception as e:
            print(f"  ⚠️ 准备度综合分析生成失败: {e}")

        print(f"\n✓ 共生成 {len(charts)} 个增强图表")

        return charts, data


if __name__ == "__main__":
    # 测试代码
    visualizer = EnhancedVisualizer(Path.cwd() / "DailyReports")
    charts, data = visualizer.generate_all_charts()
    print(f"\n生成的图表:")
    for name, path in charts:
        print(f"  - {name}: {path}")
