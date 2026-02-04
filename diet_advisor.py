#!/usr/bin/env python3
"""
金明 - 饮食建议模块
基于训练状态、时间、天气提供详细饮食建议
"""

from datetime import datetime

class DietAdvisor:
    """饮食建议顾问"""

    def __init__(self):
        self.nutrition_profile = {
            "age": 32,
            "weight_kg": 65.5,
            "height_cm": 170,
            "activity_level": "极高（自由潜水训练）",
            "goal": "优化自由潜水表现"
        }

        self.basal_metabolic_rate = 1650  # 基础代谢率（ kcal/day）
        self.daily_calorie_need = 2800   # 每日总需求（训练日）

    def get_daily_diet_plan(self, readiness_score, training_intensity, weather_temp):
        """获取每日饮食计划"""

        # 根据训练强度调整热量
        calorie_multiplier = {
            "high": 1.2,      # 高强度训练日
            "medium": 1.0,    # 中等强度训练日
            "low": 0.85       # 恢复日
        }

        multiplier = calorie_multiplier.get(training_intensity, 1.0)
        total_calories = int(self.daily_calorie_need * multiplier)

        plan = {
            "total_calories": total_calories,
            "macro_split": {
                "protein": "30%",  # 高蛋白支持肌肉恢复
                "fat": "35%",      # 优质脂肪支持激素分泌
                "carbs": "35%"     # 碳水提供训练能量
            },
            "meals": self._get_meal_details(training_intensity, weather_temp),
            "supplements": self._get_supplement_recommendations(training_intensity),
            "hydration": self._get_hydration_plan(weather_temp, training_intensity),
            "timing": self._get_nutrition_timing(training_intensity)
        }

        return plan

    def _get_meal_details(self, training_intensity, weather_temp):
        """获取每餐详细建议"""

        meals = {}

        if training_intensity == "high":
            # 高强度训练日
            meals = {
                "早餐（7:00）": {
                    "calories": 600,
                    "foods": [
                        "鸡蛋3个（水煮或煎）",
                        "燕麦粥100g + 蓝莓/草莓",
                        "全麦面包2片",
                        "坚果30g（核桃/杏仁）",
                        "黑咖啡或绿茶"
                    ],
                    "supplements": ["NMN22000 1粒", "益生菌1粒", "鱼油2粒"],
                    "note": "高蛋白早餐，为上午训练提供能量"
                },
                "训练前加餐（10:00）": {
                    "calories": 300,
                    "foods": [
                        "香蕉1根",
                        "MCT油15ml",
                        "BCAA 5g（可选）"
                    ],
                    "supplements": [],
                    "note": "快速碳水和MCT油，提升训练表现"
                },
                "午餐（12:30）": {
                    "calories": 800,
                    "foods": [
                        "深海鱼（三文鱼/鲭鱼）200g 或 鸡胸肉200g",
                        "糙米/藜麦 150g",
                        "西兰花/菠菜 200g",
                        "橄榄油 1汤匙",
                        "柠檬汁调味"
                    ],
                    "supplements": ["维生素D3 2粒"],
                    "note": "优质蛋白质和复合碳水，支持恢复"
                },
                "训练后恢复（16:00）": {
                    "calories": 400,
                    "foods": [
                        "乳清蛋白粉30g 或 鸡蛋白3个",
                        "香蕉1根",
                        "蜂蜜1茶匙",
                        "电解质水500ml"
                    ],
                    "supplements": ["肌酸5g（训练日）"],
                    "note": "快速蛋白质和碳水，促进肌肉恢复"
                },
                "晚餐（19:00）": {
                    "calories": 700,
                    "foods": [
                        "瘦牛肉/三文鱼 180g",
                        "红薯/南瓜 200g",
                        "混合蔬菜沙拉（大量）",
                        "橄榄油 1汤匙",
                        "牛油果半个"
                    ],
                    "supplements": ["镁 2粒"],
                    "note": "易消化蛋白质，避免影响睡眠"
                }
            }

        elif training_intensity == "medium":
            # 中等强度训练日
            meals = {
                "早餐（7:00）": {
                    "calories": 550,
                    "foods": [
                        "鸡蛋2个",
                        "燕麦粥80g",
                        "全麦面包1片",
                        "坚果20g"
                    ],
                    "supplements": ["NMN22000 1粒", "益生菌1粒", "鱼油2粒"],
                    "note": "均衡营养早餐"
                },
                "午餐（12:30）": {
                    "calories": 750,
                    "foods": [
                        "鸡胸肉/鱼肉 180g",
                        "糙米/藜麦 130g",
                        "蔬菜 200g",
                        "橄榄油 1汤匙"
                    ],
                    "supplements": ["维生素D3 2粒"],
                    "note": "蛋白质和复合碳水"
                },
                "训练前加餐（15:30）": {
                    "calories": 250,
                    "foods": ["香蕉1根", "坚果15g"],
                    "supplements": [],
                    "note": "训练能量补充"
                },
                "训练后（17:30）": {
                    "calories": 350,
                    "foods": ["蛋白质30g", "水果1份"],
                    "supplements": [],
                    "note": "恢复营养"
                },
                "晚餐（19:00）": {
                    "calories": 650,
                    "foods": [
                        "瘦肉/鱼 150g",
                        "红薯 150g",
                        "大量蔬菜",
                        "橄榄油 1汤匙"
                    ],
                    "supplements": ["镁 2粒"],
                    "note": "清淡晚餐"
                }
            }

        else:  # low intensity / recovery day
            # 恢复日
            meals = {
                "早餐（7:30）": {
                    "calories": 500,
                    "foods": [
                        "鸡蛋2个",
                        "希腊酸奶 + 浆果",
                        "坚果20g",
                        "全麦面包1片"
                    ],
                    "supplements": ["NMN22000 1粒", "益生菌1粒", "鱼油2粒"],
                    "note": "轻松早餐"
                },
                "早加餐（10:00）": {
                    "calories": 150,
                    "foods": ["水果1份", "坚果10g"],
                    "supplements": [],
                    "note": "健康零食"
                },
                "午餐（12:30）": {
                    "calories": 700,
                    "foods": [
                        "鱼肉/鸡肉 150g",
                        "大量蔬菜沙拉",
                        "糙米100g",
                        "橄榄油 + 柠檬汁"
                    ],
                    "supplements": ["维生素D3 2粒"],
                    "note": "清淡午餐"
                },
                "下午茶（15:30）": {
                    "calories": 200,
                    "foods": ["坚果15g", "水果1份"],
                    "supplements": [],
                    "note": "抗氧化零食"
                },
                "晚餐（18:30）": {
                    "calories": 600,
                    "foods": [
                        "清淡汤品",
                        "蒸鱼/鸡胸肉 150g",
                        "蔬菜 250g",
                        "少量红薯"
                    ],
                    "supplements": ["镁 2粒"],
                    "note": "易消化，早晚餐"
                }
            }

        return meals

    def _get_supplement_recommendations(self, training_intensity):
        """获取补剂建议"""
        return {
            "每日必需": [
                "NMN22000 1粒（早晨空腹）",
                "益生菌 1粒（空腹）",
                "鱼油 2粒（早餐后）",
                "维生素D3 2000IU（午餐后）",
                "镁 400mg（睡前）"
            ],
            "训练日额外": [
                "肌酸 5g（训练后）",
                "BCAA 5-10g（训练中，可选）",
                "电解质（训练超过1小时）"
            ],
            "异维A酸": "隔日服用（偶数日10mg）"
        }

    def _get_hydration_plan(self, weather_temp, training_intensity):
        """获取水分补充计划"""
        base_water = 65.5 * 35  # 体重 × 35ml = 约2.3L

        # 根据温度调整
        if weather_temp > 25:
            temp_multiplier = 1.3
        elif weather_temp > 15:
            temp_multiplier = 1.1
        else:
            temp_multiplier = 1.0

        # 根据训练强度调整
        training_multiplier = {
            "high": 1.5,
            "medium": 1.2,
            "low": 1.0
        }.get(training_intensity, 1.0)

        total_water_ml = int(base_water * temp_multiplier * training_multiplier)

        return {
            "total_water_ml": total_water_ml,
            "total_liters": round(total_water_ml / 1000, 1),
            "schedule": [
                f"起床：500ml温水 + 柠檬",
                f"早餐：300ml",
                f"训练前：500ml（提前1小时）",
                f"训练中：200-250ml/每15分钟",
                f"训练后：500ml + 电解质",
                f"下午：500ml",
                f"晚餐：300ml",
                f"睡前：200ml"
            ],
            "electrolytes": "训练日添加电解质粉（钠、钾、镁）",
            "note": f"尿色应保持淡黄色，总量约{round(total_water_ml/1000, 1)}升"
        }

    def _get_nutrition_timing(self, training_intensity):
        """获取营养时机建议"""
        if training_intensity == "high":
            return {
                "训练前": "2-3小时前完成正餐，30分钟前轻食（香蕉+MCT油）",
                "训练中": "超过1小时补充电解质水，每15分钟250ml",
                "训练后": "30分钟内补充蛋白质30g + 碳水40-50g（黄金窗口期）",
                "睡前": "3-4小时完成晚餐，可补充镁助眠"
            }
        elif training_intensity == "medium":
            return {
                "训练前": "2小时前完成正餐",
                "训练后": "1小时内补充蛋白质20-30g",
                "睡前": "2-3小时完成晚餐"
            }
        else:
            return {
                "训练前": "无需特殊准备",
                "训练后": "正常饮食即可",
                "睡前": "提前2-3小时完成晚餐，补充镁"
            }

    def get_food_avoidances(self):
        """获取应避免的食物"""
        return {
            "因异维A酸需避免": [
                "❌ 维生素A补充剂",
                "❌ 动物肝脏",
                "❌ 高剂量β-胡萝卜素补充"
            ],
            "自由潜水运动员应避免": [
                "❌ 训练前大量脂肪（影响消化）",
                "❌ 训练前高纤维（避免胀气）",
                "❌ 酒精（影响恢复和表现）",
                "❌ 过量咖啡因（影响心率）",
                "❌ 精制糖（炎症反应）"
            ],
            "训练日特别注意": [
                "❌ 训练前2小时大量进食",
                "❌ 训练前辛辣/油腻食物",
                "❌ 训练中过量饮水（胃部不适）"
            ]
        }

    def generate_diet_recommendations_md(self, readiness_score, recovery_index, weather_temp):
        """生成饮食建议Markdown"""

        # 判断训练强度
        if readiness_score >= 85 and recovery_index >= 75:
            intensity = "high"
            intensity_name = "高强度训练日"
        elif readiness_score >= 70:
            intensity = "medium"
            intensity_name = "中等强度训练日"
        else:
            intensity = "low"
            intensity_name = "恢复日"

        plan = self.get_daily_diet_plan(readiness_score, intensity, weather_temp)
        hydration = self._get_hydration_plan(weather_temp, intensity)
        avoidances = self.get_food_avoidances()

        md = f"""## 🍽️ 每日饮食建议

**训练类型：** {intensity_name}
**总热量需求：** {plan['total_calories']} kcal
**营养分配：** 蛋白质 {plan['macro_split']['protein']} | 脂肪 {plan['macro_split']['fat']} | 碳水 {plan['macro_split']['carbs']}

### 📋 每餐详细计划

"""

        for meal_name, meal_info in plan['meals'].items():
            md += f"""#### {meal_name}
**热量：** {meal_info['calories']} kcal

**食物清单：**
"""
            for food in meal_info['foods']:
                md += f"- {food}\n"

            if meal_info['supplements']:
                md += f"\n**补剂：** {', '.join(meal_info['supplements'])}\n"

            md += f"\n**说明：** {meal_info['note']}\n\n"

        md += f"""### 💧 水分补充计划

**每日总量：** {hydration['total_liters']} 升

**时间表：**
"""
        for schedule_item in hydration['schedule']:
            md += f"- {schedule_item}\n"

        md += f"""
**电解质补充：** {hydration['electrolytes']}

**注意：** {hydration['note']}

### ⏰ 营养时机建议

"""
        timing = plan['timing']
        for key, value in timing.items():
            md += f"**{key}：** {value}\n"

        md += "\n### 💊 补剂清单\n\n"

        supplements = plan['supplements']
        md += "**每日必需：**\n"
        for item in supplements['每日必需']:
            md += f"- {item}\n"

        if intensity == "high":
            md += "\n**训练日额外：**\n"
            for item in supplements['训练日额外']:
                md += f"- {item}\n"

        md += f"\n**异维A酸：** {supplements['异维A酸']}\n"

        md += "\n### 🚫 应避免的食物\n\n"

        for category, items in avoidances.items():
            md += f"**{category}：**\n"
            for item in items:
                md += f"{item}\n"
            md += "\n"

        return md

def main():
    advisor = DietAdvisor()

    # 测试生成
    md = advisor.generate_diet_recommendations_md(
        readiness_score=86,
        recovery_index=100,
        weather_temp=11.7
    )

    print(md)

if __name__ == "__main__":
    main()
