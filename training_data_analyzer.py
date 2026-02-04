#!/usr/bin/env python3
"""
金明 - 训练数据分析模块
整合训练数据、成绩记录、个性化建议
"""

from datetime import datetime
from pathlib import Path
import json

class TrainingDataAnalyzer:
    """训练数据分析器"""

    def __init__(self):
        self.personal_records = {
            "lung_capacity_ml": {
                "best": 7653,
                "date": "2024.5.27",
                "recent": 7238,
                "recent_date": "2024.6.3"
            },
            "swimming_1000m_breaststroke": {
                "best_time": "17:56",
                "best_date": "2025.9.25",
                "best_pace_per_100m": "1:47",
                "improvement": "15%"
            },
            "championship_medals": {
                "total": 6,
                "note": "CMAS + AIDA世锦赛"
            },
            "resting_hr": {
                "range": "54-56",
                "unit": "bpm"
            },
            "hrv": {
                "range": "34-36",
                "unit": "ms"
            }
        }

        self.training_insights = {
            "best_conditions": {
                "readiness_score": "≥85",
                "hrv": "≥34",
                "recovery_index": "≥75",
                "notes": "在这些指标下，创造了7.6L肺活量PB和游泳PB"
            },
            "performance_patterns": [
                "持续系统训练3个月可提升肺活量400-500ml",
                "饮酒（VSOP）后第二天肺活量下降约200ml",
                "3个月不训练会退步400-500ml",
                "游泳成绩从21分7秒提升到17分56秒（约15%提升）"
            ],
            "upcoming_competitions": [
                "2025年世锦赛 - 需要重点关注备赛计划执行"
            ],
            "training_phase": "备赛期"
        }

        self.recommendations = {
            "high_readiness": {
                "threshold": 85,
                "training_types": ["高强度泳池训练", "1000米蛙泳测试", "技术突破"],
                "note": "接近PB状态，可以尝试突破个人记录"
            },
            "moderate_readiness": {
                "threshold": 70,
                "training_types": ["泳池基础训练", "技术练习", "陆地训练"],
                "note": "维持系统训练，巩固技术"
            },
            "low_recovery": {
                "threshold": 50,
                "training_types": ["瑜伽", "拉伸", "轻度活动"],
                "note": "恢复不足，避免高强度训练"
            }
        }

    def analyze_current_status(self, health_data):
        """基于当前健康数据生成训练建议"""

        readiness_score = health_data.get("readiness", {}).get("score", 0)
        hrv_balance = health_data.get("readiness", {}).get("contributors", {}).get("hrv_balance", 0)
        recovery_index = health_data.get("readiness", {}).get("contributors", {}).get("recovery_index", 0)
        sleep_score = health_data.get("sleep", {}).get("score", 0)

        analysis = {
            "current_readiness": readiness_score,
            "status": "",
            "recommendation": "",
            "training_types": [],
            "confidence": "",
            "comparison_to_best": "",
            "performance_prediction": ""
        }

        # 判断当前状态
        if readiness_score >= 85 and recovery_index >= 75:
            analysis["status"] = "🔥 最佳状态"
            analysis["recommendation"] = "今日是挑战个人记录的好时机！你的状态接近创造7.6L肺活量PB时的水平"
            analysis["training_types"] = self.recommendations["high_readiness"]["training_types"]
            analysis["confidence"] = "高"
            analysis["comparison_to_best"] = f"当前准备度 {readiness_score}，接近最佳状态（≥85）"
            analysis["performance_prediction"] = "预测表现：优秀，有PB潜力"

        elif readiness_score >= 70 and recovery_index >= 60:
            analysis["status"] = "💪 训练状态"
            analysis["recommendation"] = "适合系统训练，巩固技术，为2025世锦赛储备体能"
            analysis["training_types"] = self.recommendations["moderate_readiness"]["training_types"]
            analysis["confidence"] = "中"
            analysis["comparison_to_best"] = f"当前准备度 {readiness_score}，属于良好训练状态"
            analysis["performance_prediction"] = "预测表现：良好，稳定进步"

        elif recovery_index < 50:
            analysis["status"] = "⚠️ 恢复不足"
            analysis["recommendation"] = "建议轻量训练或休息。低恢复状态训练会增加受伤风险，影响后续备赛"
            analysis["training_types"] = self.recommendations["low_recovery"]["training_types"]
            analysis["confidence"] = "高"
            analysis["comparison_to_best"] = f"恢复指数 {recovery_index} 低于最佳状态（≥75）"
            analysis["performance_prediction"] = "预测表现：亚于最佳，建议调整"

        else:
            analysis["status"] = "✓ 稳定状态"
            analysis["recommendation"] = "维持常规训练，按照备赛计划执行"
            analysis["training_types"] = ["常规训练", "技术维护"]
            analysis["confidence"] = "中"
            analysis["comparison_to_best"] = f"当前准备度 {readiness_score}"
            analysis["performance_prediction"] = "预测表现：稳定"

        return analysis

    def get_personal_best_summary(self):
        """获取个人最好成绩总结"""
        return f"""
### 🏆 个人最好成绩 (PB)

| 项目 | 成绩 | 日期 |
|------|------|------|
| 肺活量 | **7,653 ml** | 2024.5.27 |
| 蛙泳 1000m | **17分56秒** (配速 1:47/100m) | 2025.9.25 |
| 世锦赛奖牌 | **6枚** | CMAS + AIDA |
| 静息心率 | **54-56 bpm** | 日常平均 |
| HRV | **34-36 ms** | 日常平均 |

### 📈 训练洞察

**最佳表现条件：**
- 准备度 ≥ 85
- HRV ≥ 34
- 恢复指数 ≥ 75

**表现模式：**
- 系统训练3个月 → 肺活量提升400-500ml
- 饮酒后第二天 → 肺活量下降约200ml
- 停止训练3个月 → 退步400-500ml
- 游泳成绩提升：21分7秒 → 17分56秒（15%进步）

**当前阶段：** 2025世锦赛备赛期
"""

def main():
    analyzer = TrainingDataAnalyzer()
    print(analyzer.get_personal_best_summary())

if __name__ == "__main__":
    main()
