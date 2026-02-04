#!/usr/bin/env python3
"""
金明 - 图表生成模块
使用matplotlib生成专业健康数据图表
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class HealthChartGenerator:
    """健康图表生成器"""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.charts_dir = self.output_dir / "charts"
        # 确保父目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir.mkdir(exist_ok=True)

    def generate_readiness_radar_chart(self, health_data, detailed_analysis=None):
        """生成准备度雷达图"""
        readiness = health_data.get("readiness", {})
        contributors = readiness.get("contributors", {})

        categories = ['HRV平衡', '恢复指数', '静息心率', '睡眠平衡', '活动平衡']
        values = [
            contributors.get('hrv_balance', 0),
            contributors.get('recovery_index', 0),
            contributors.get('resting_heart_rate', 0),
            contributors.get('sleep_balance', 0),
            contributors.get('activity_balance', 0)
        ]

        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))

        # 设置角度
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # 闭合图形
        angles += angles[:1]

        # 绘制雷达图
        ax.plot(angles, values, 'o-', linewidth=2, color='#667eea', label='当前状态')
        ax.fill(angles, values, alpha=0.25, color='#667eea')

        # 添加目标区域（优秀水平）
        target_values = [85] * len(categories)
        target_values += target_values[:1]
        ax.plot(angles, target_values, '--', linewidth=1, color='gray', alpha=0.5, label='优秀水平 (85)')
        ax.fill(angles, target_values, alpha=0.1, color='gray')

        # 设置图表
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.7)

        # 添加标题
        readiness_score = readiness.get('score', 0)
        ax.set_title(f'健康指标雷达图\n准备度: {readiness_score}/100',
                    size=14, weight='bold', pad=20)

        # 添加图例
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        # 保存
        output_file = self.charts_dir / "readiness_radar.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ 雷达图已生成: {output_file}")
        return output_file

    def generate_sleep_quality_chart(self, health_data):
        """生成睡眠质量图表"""
        sleep = health_data.get("sleep", {})
        contributors = sleep.get("contributors", {})

        # 睡眠指标
        metrics = ['总睡眠\n质量', '深睡\n质量', 'REM\n质量', '睡眠\n效率', '入睡\n速度', '睡眠\n安享度', '睡眠\n规律']
        values = [
            contributors.get('total_sleep', 0),
            contributors.get('deep_sleep', 0),
            contributors.get('rem_sleep', 0),
            contributors.get('efficiency', 0),
            contributors.get('latency', 0),
            contributors.get('restfulness', 0),
            contributors.get('timing', 0)
        ]

        # 创建柱状图
        fig, ax = plt.subplots(figsize=(12, 6))

        colors = []
        for v in values:
            if v >= 80:
                colors.append('#10b981')  # 绿色
            elif v >= 60:
                colors.append('#3b82f6')  # 蓝色
            elif v >= 40:
                colors.append('#f59e0b')  # 橙色
            else:
                colors.append('#ef4444')  # 红色

        bars = ax.bar(metrics, values, color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10, weight='bold')

        # 设置y轴
        ax.set_ylim(0, 100)
        ax.set_ylabel('分数', fontsize=11, weight='bold')
        ax.set_title(f'睡眠质量详细分析 (总分: {sleep.get("score", 0)}/100)',
                    size=14, weight='bold', pad=15)

        # 添加网格
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        # 保存
        output_file = self.charts_dir / "sleep_quality.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ 睡眠图表已生成: {output_file}")
        return output_file

    def generate_weekly_trend_chart(self, oura_data_list):
        """生成周趋势图表"""
        if not oura_data_list or len(oura_data_list) < 7:
            print("⚠️ 数据不足7天，跳过周趋势图")
            return None

        # 准备数据
        dates = [d.get('day', '') for d in oura_data_list[-7:]]
        readiness_scores = [d.get('score', 0) for d in oura_data_list[-7:]]
        sleep_scores = [d.get('sleep', {}).get('score', 0) for d in oura_data_list[-7:]]

        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # 准备度趋势
        ax1.plot(range(7), readiness_scores, marker='o', linewidth=2.5,
                markersize=8, color='#667eea', label='准备度')
        ax1.fill_between(range(7), readiness_scores, alpha=0.3, color='#667eea')
        ax1.axhline(y=85, color='green', linestyle='--', alpha=0.5, label='优秀线')
        ax1.set_ylim(0, 100)
        ax1.set_ylabel('准备度分数', fontsize=11, weight='bold')
        ax1.set_title('7日准备度趋势', size=13, weight='bold')
        ax1.grid(alpha=0.3, linestyle='--')
        ax1.legend()
        ax1.set_xticks(range(7))
        ax1.set_xticklabels([d[-5:] for d in dates], rotation=45)

        # 睡眠趋势
        ax2.plot(range(7), sleep_scores, marker='s', linewidth=2.5,
                markersize=8, color='#8b5cf6', label='睡眠分数')
        ax2.fill_between(range(7), sleep_scores, alpha=0.3, color='#8b5cf6')
        ax2.axhline(y=85, color='green', linestyle='--', alpha=0.5, label='优秀线')
        ax2.set_ylim(0, 100)
        ax2.set_ylabel('睡眠分数', fontsize=11, weight='bold')
        ax2.set_title('7日睡眠质量趋势', size=13, weight='bold')
        ax2.grid(alpha=0.3, linestyle='--')
        ax2.legend()
        ax2.set_xticks(range(7))
        ax2.set_xticklabels([d[-5:] for d in dates], rotation=45)

        plt.tight_layout()

        # 保存
        output_file = self.charts_dir / "weekly_trend.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ 趋势图已生成: {output_file}")
        return output_file

    def generate_activity_pie_chart(self, health_data):
        """生成活动分布饼图"""
        activity = health_data.get("activity", {})
        daily_activity = activity.get('daily_activity', {})

        # 活动类型
        if not daily_activity:
            # 使用模拟数据
            labels = ['高活动', '中等活动', '低活动', '休息/睡眠']
            sizes = [35, 25, 20, 20]
            colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
        else:
            labels = ['高活动', '中等活动', '低活动', '休息/睡眠']
            sizes = [
                daily_activity.get('high', 30),
                daily_activity.get('medium', 25),
                daily_activity.get('low', 20),
                daily_activity.get('rest', 25)
            ]
            colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']

        # 创建饼图
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                              autopct='%1.1f%%',
                                              pctdistance=0.85,
                                              explode=(0.05, 0, 0, 0),
                                              shadow=True, startangle=90)

        # 设置文本样式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
            autotext.set_fontsize(12)

        for text in texts:
            text.set_fontsize(13)
            text.set_weight('bold')

        ax.set_title('今日活动分布', size=15, weight='bold', pad=20)

        # 保存
        output_file = self.charts_dir / "activity_distribution.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ 活动分布图已生成: {output_file}")
        return output_file

    def generate_training_gauge_chart(self, readiness_score):
        """生成训练准备度仪表盘"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # 创建半圆仪表盘
        theta = np.linspace(0, np.pi, 100)
        radii = 10 * np.ones_like(theta)

        # 背景圆弧（红色到黄色到绿色）
        colors = ['#ef4444'] * 33 + ['#f59e0b'] * 33 + ['#10b981'] * 34
        for i in range(100):
            ax.bar(theta[i], radii[i], width=0.032, color=colors[i],
                   edgecolor='white', linewidth=0.5)

        # 指针
        score_angle = np.pi * (1 - readiness_score / 100)
        ax.arrow(0, 0, np.cos(score_angle) * 8.5, np.sin(score_angle) * 8.5,
                 head_width=1.5, head_length=2, fc='black', ec='black')

        # 设置
        ax.set_ylim(0, 12)
        ax.set_xlim(-0.5, np.pi + 0.5)
        ax.axis('off')

        # 添加分数
        ax.text(0.5, 0.5, f'{readiness_score}',
                transform=ax.transAxes,
                ha='center', va='center',
                fontsize=48, weight='bold')

        ax.text(0.5, 0.35, '训练准备度',
                transform=ax.transAxes,
                ha='center', va='center',
                fontsize=16, weight='bold')

        # 添加状态标签
        if readiness_score >= 85:
            status = '🔥 最佳状态'
            status_color = '#10b981'
        elif readiness_score >= 70:
            status = '✓ 良好状态'
            status_color = '#3b82f6'
        elif readiness_score >= 55:
            status = '🟡 一般状态'
            status_color = '#f59e0b'
        else:
            status = '⚠️ 需休息'
            status_color = '#ef4444'

        ax.text(0.5, 0.2, status,
                transform=ax.transAxes,
                ha='center', va='center',
                fontsize=18, weight='bold',
                color=status_color)

        ax.set_title('今日训练准备度', size=15, weight='bold', pad=20)

        # 保存
        output_file = self.charts_dir / "readiness_gauge.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ 仪表盘图已生成: {output_file}")
        return output_file

def main():
    """测试图表生成"""
    generator = HealthChartGenerator("/tmp/test_charts")

    # 模拟数据
    health_data = {
        "readiness": {
            "score": 86,
            "contributors": {
                "hrv_balance": 86,
                "recovery_index": 100,
                "resting_heart_rate": 89,
                "sleep_balance": 97,
                "activity_balance": 79
            }
        },
        "sleep": {
            "score": 70,
            "contributors": {
                "total_sleep": 71,
                "deep_sleep": 74,
                "rem_sleep": 76,
                "efficiency": 96,
                "latency": 72,
                "restfulness": 74,
                "timing": 23
            }
        },
        "activity": {
            "daily_activity": {
                "high": 35,
                "medium": 25,
                "low": 20,
                "rest": 20
            }
        }
    }

    # 生成所有图表
    print("🎨 生成图表...")
    generator.generate_readiness_radar_chart(health_data)
    generator.generate_sleep_quality_chart(health_data)
    generator.generate_activity_pie_chart(health_data)
    generator.generate_training_gauge_chart(86)
    print("✓ 所有图表生成完成！")

if __name__ == "__main__":
    main()
