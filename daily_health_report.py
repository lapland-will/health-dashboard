#!/usr/bin/env python3
"""
金明 - Oura Ring 每日健康报告生成器
功能：生成今日完整的健康报告，包括训练建议
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Oura API 配置
ACCESS_TOKEN = "DUC6D3LWLLNOWXK6IBNVEFS7IH445TIV"
BASE_URL = "https://api.ouraring.com/v2"

class OuraDailyReport:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.report_dir = Path.cwd() / "DailyReports"
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def make_request(self, endpoint, params=None):
        """发起API请求"""
        try:
            response = requests.get(
                f"{BASE_URL}/{endpoint}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API请求失败 ({endpoint}): {e}")
            return None

    def get_daily_readiness(self):
        """获取今日准备度数据"""
        print("获取准备度数据...")
        data = self.make_request(
            "usercollection/daily_readiness",
            {
                "start_date": self.yesterday,
                "end_date": self.today
            }
        )

        if data and "data" in data:
            # 获取最新一天的数据
            latest = data["data"][-1] if data["data"] else None
            if latest:
                return {
                    "date": latest.get("day"),
                    "score": latest.get("score"),
                    "temperature_delta": latest.get("contributors", {}).get("temperature_delta", 0),
                    "hrv_balance": latest.get("contributors", {}).get("hrv_balance", 0),
                    "recovery_index": latest.get("contributors", {}).get("recovery_index", 0),
                    "resting_heart_rate": latest.get("contributors", {}).get("resting_heart_rate", 0),
                    "sleep_balance": latest.get("contributors", {}).get("sleep_balance", 0),
                    "previous_day_activity": latest.get("contributors", {}).get("previous_day_activity", 0),
                    "activity_balance": latest.get("contributors", {}).get("activity_balance", 0)
                }
        return None

    def get_daily_sleep(self):
        """获取今日睡眠数据"""
        print("获取睡眠数据...")
        data = self.make_request(
            "usercollection/daily_sleep",
            {
                "start_date": self.yesterday,
                "end_date": self.today
            }
        )

        if data and "data" in data:
            latest = data["data"][-1] if data["data"] else None
            if latest:
                return {
                    "date": latest.get("day"),
                    "score": latest.get("score"),
                    "total_sleep_duration": latest.get("total_sleep_duration", 0) / 3600,  # 转换为小时
                    "total_rem": latest.get("total_rem", 0) / 3600,
                    "total_deep": latest.get("total_deep", 0) / 3600,
                    "sleep_efficiency": latest.get("sleep_efficiency", 0),
                    "onset_latency": latest.get("onset_latency", 0) / 60,  # 转换为分钟
                    "average_hr": latest.get("average_hr", 0),
                    "lowest_hr": latest.get("lowest_hr", 0),
                    "average_hrv": latest.get("average_hrv", 0)
                }
        return None

    def get_daily_activity(self):
        """获取今日活动数据"""
        print("获取活动数据...")
        data = self.make_request(
            "usercollection/daily_activity",
            {
                "start_date": self.yesterday,
                "end_date": self.today
            }
        )

        if data and "data" in data:
            latest = data["data"][-1] if data["data"] else None
            if latest:
                return {
                    "date": latest.get("day"),
                    "score": latest.get("score"),
                    "steps": latest.get("steps", 0),
                    "total_calories": latest.get("total_calories", 0),
                    "active_calories": latest.get("active_calories", 0),
                    "distance": latest.get("distance_km", 0),
                    "equivalent_walking_distance": latest.get("equivalent_walking_distance_km", 0)
                }
        return None

    def get_heart_rate_today(self):
        """获取今日心率数据"""
        print("获取今日心率数据...")
        data = self.make_request(
            "usercollection/heartrate",
            {
                "start_datetime": f"{self.today}T00:00:00Z",
                "end_datetime": f"{self.today}T23:59:59Z"
            }
        )

        if data and "data" in data and data["data"]:
            heart_rates = [item.get("bpm", 0) for item in data["data"]]
            if heart_rates:
                return {
                    "average": sum(heart_rates) / len(heart_rates),
                    "min": min(heart_rates),
                    "max": max(heart_rates),
                    "samples": len(heart_rates)
                }
        return None

    def get_training_recommendation(self, readiness, sleep, activity):
        """基于数据生成训练建议"""
        recommendations = []

        # 准备度评估
        if readiness:
            score = readiness["score"]
            if score >= 85:
                recommendations.append({
                    "level": "✓ 高强度",
                    "readiness": f"准备度 {score}/100 - 状态优秀",
                    "training": "可以进行高强度闭气训练、深度挑战、技术精练"
                })
            elif score >= 70:
                recommendations.append({
                    "level": "✓ 中等强度",
                    "readiness": f"准备度 {score}/100 - 状态良好",
                    "training": "适合中等强度训练，注意监测身体反应"
                })
            elif score >= 55:
                recommendations.append({
                    "level": "⚠️ 低强度",
                    "readiness": f"准备度 {score}/100 - 状态一般",
                    "training": "建议轻度训练或休息，优先恢复"
                })
            else:
                recommendations.append({
                    "level": "❌ 休息",
                    "readiness": f"准备度 {score}/100 - 状态不佳",
                    "training": "建议完全休息，避免高强度训练"
                })

        # HRV评估
        if readiness:
            hrv = readiness["hrv_balance"]
            if hrv < 60:
                recommendations.append({
                    "level": "⚠️ 注意",
                    "hrv": f"HRV平衡 {hrv}/100 - 偏低",
                    "advice": "可能存在疲劳累积，建议减少训练强度"
                })
            elif hrv >= 80:
                recommendations.append({
                    "level": "✓",
                    "hrv": f"HRV平衡 {hrv}/100 - 优秀",
                    "advice": "自主神经系统恢复良好，适合训练"
                })

        # 睡眠评估
        if sleep:
            sleep_score = sleep["score"]
            if sleep_score < 70:
                recommendations.append({
                    "level": "⚠️",
                    "sleep": f"睡眠 {sleep_score}/100 - 需改善",
                    "advice": "昨晚睡眠质量不佳，今天建议降低训练强度"
                })

        return recommendations

    def generate_report(self):
        """生成完整健康报告"""
        print("=" * 60)
        print("金明 - Oura Ring 每日健康报告")
        print("=" * 60)

        # 获取数据
        readiness = self.get_daily_readiness()
        sleep = self.get_daily_sleep()
        activity = self.get_daily_activity()
        heart_rate = self.get_heart_rate_today()

        # 生成训练建议
        training_recommendations = self.get_training_recommendation(readiness, sleep, activity)

        # 创建Markdown报告
        report_content = f"""# 金明 - 今日健康报告

**日期：** {self.today}
**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 今日健康评分

### 准备度 (Readiness)

"""

        if readiness:
            score = readiness["score"]
            status_emoji = "⭐" if score >= 85 else "✓" if score >= 70 else "⚠️"
            report_content += f"""**分数：** {score}/100 {status_emoji}

| 指标 | 数值 |
|------|------|
| HRV平衡 | {readiness['hrv_balance']}/100 |
| 恢复指数 | {readiness['recovery_index']}/100 |
| 静息心率 | {readiness['resting_heart_rate']}/100 |
| 睡眠平衡 | {readiness['sleep_balance']}/100 |
| 活动平衡 | {readiness['activity_balance']}/100 |

"""
        else:
            report_content += "⚠️ 今日暂无数据\n\n"

        # 睡眠数据
        report_content += "### 睡眠质量\n\n"

        if sleep:
            total_sleep = sleep['total_sleep_duration'] if sleep['total_sleep_duration'] > 0 else 1
            deep_percent = sleep['total_deep']/total_sleep*100 if total_sleep > 0 else 0
            rem_percent = sleep['total_rem']/total_sleep*100 if total_sleep > 0 else 0

            report_content += f"""**分数：** {sleep['score']}/100

| 指标 | 数值 |
|------|------|
| 总睡眠时长 | {sleep['total_sleep_duration']:.1f} 小时 |
| 深度睡眠 | {sleep['total_deep']:.1f} 小时 ({deep_percent:.1f}%) |
| 快速眼动睡眠 | {sleep['total_rem']:.1f} 小时 ({rem_percent:.1f}%) |
| 睡眠效率 | {sleep['sleep_efficiency']:.1f}% |
| 入睡时间 | {sleep['onset_latency']:.1f} 分钟 |
| 平均心率 | {sleep['average_hr']:.0f} bpm |
| 最低心率 | {sleep['lowest_hr']:.0f} bpm |
| 平均HRV | {sleep['average_hrv']:.0f} ms |

"""
        else:
            report_content += "⚠️ 昨晚暂无睡眠数据\n\n"

        # 活动数据
        report_content += "### 活动数据\n\n"

        if activity:
            report_content += f"""**分数：** {activity['score']}/100

| 指标 | 数值 |
|------|------|
| 步数 | {activity['steps']:,} 步 |
| 总消耗 | {activity['total_calories']:.0f} 千卡 |
| 活动消耗 | {activity['active_calories']:.0f} 千卡 |
| 距离 | {activity['distance']:.2f} 公里 |

"""
        else:
            report_content += "⚠️ 今日暂无活动数据\n\n"

        # 今日心率
        if heart_rate:
            report_content += f"""### 今日心率

| 指标 | 数值 |
|------|------|
| 平均心率 | {heart_rate['average']:.0f} bpm |
| 最低心率 | {heart_rate['min']:.0f} bpm |
| 最高心率 | {heart_rate['max']:.0f} bpm |
| 采样次数 | {heart_rate['samples']} 次 |

"""

        # 训练建议
        report_content += "---\n\n## 🎯 自由潜水训练建议\n\n"

        if training_recommendations:
            for rec in training_recommendations:
                report_content += f"### {rec.get('level', '')}\n\n"
                for key, value in rec.items():
                    if key != "level":
                        report_content += f"**{key}：** {value}\n\n"
        else:
            report_content += "暂无建议（等待更多数据）\n\n"

        # 补剂提醒
        report_content += "---\n\n## 💊 补剂提醒\n\n"

        # 检查是否是服药日（基于日期的奇偶）
        day_of_month = datetime.now().day
        if day_of_month % 2 == 0:  # 偶数日
            report_content += "**今日补剂：**\n\n"
            report_content += "- ☑ 异维A酸 10mg（今日服药日）\n"
        else:  # 奇数日
            report_content += "**今日补剂：**\n\n"
            report_content += "- ☐ 异维A酸 10mg（今日非服药日）\n"

        report_content += "- ☑ NMN22000 1粒\n"
        report_content += "- ☑ 益生菌\n"
        report_content += "- ☑ 鱼油\n"
        report_content += "- ☑ 镁（睡前）\n"
        report_content += "- ☑ 维生素D3\n"

        if activity and activity['score'] > 0:
            report_content += "- ☑ 肌酸 3g（今日有活动）\n"

        report_content += """

---
## 📋 数据文件位置

- **Markdown报告**：`""" + str(self.report_dir.relative_to(Path.cwd())) + f"""/daily_report_{self.today}.md`
- **JSON数据**：`""" + str(self.report_dir.relative_to(Path.cwd())) + f"""/daily_report_{self.today}.json`

---
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源：Oura Ring Gen 3*
"""

        # 保存Markdown报告
        report_file = self.report_dir / f"daily_report_{self.today}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n✓ Markdown报告已保存: {report_file}")

        # 保存JSON报告
        json_data = {
            "date": self.today,
            "generated_at": datetime.now().isoformat(),
            "readiness": readiness,
            "sleep": sleep,
            "activity": activity,
            "heart_rate": heart_rate,
            "training_recommendations": training_recommendations
        }

        json_file = self.report_dir / f"daily_report_{self.today}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"✓ JSON报告已保存: {json_file}")

        return report_content

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("金明 - Oura Ring 每日健康报告生成器")
    print("=" * 60 + "\n")

    report_generator = OuraDailyReport()

    # 生成报告
    report_content = report_generator.generate_report()

    print("\n" + "=" * 60)
    print("✓ 每日健康报告生成完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
