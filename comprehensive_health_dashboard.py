#!/usr/bin/env python3
"""
金明 - 全面健康报告看板
功能：生成包含健康数据、天气、空气质量、训练建议的综合看板
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Oura API 配置
ACCESS_TOKEN = "DUC6D3LWLLNOWXK6IBNVEFS7IH445TIV"
BASE_URL = "https://api.ouraring.com/v2"

# 城市配置（用于天气和空气质量）
CITY = "Shanghai"  # 可以根据实际位置修改

class ComprehensiveHealthDashboard:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        self.today = datetime.now()
        self.today_str = self.today.strftime("%Y-%m-%d")
        self.yesterday_str = (self.today - timedelta(days=1)).strftime("%Y-%m-%d")
        self.dashboard_dir = Path.cwd() / "DailyReports"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)

        self.health_data = {}
        self.weather_data = {}
        self.aqi_data = {}

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

    def get_oura_data(self):
        """获取Oura Ring所有数据"""
        print("📊 获取Oura Ring数据...")

        # 准备度数据
        readiness = self.make_request(
            "usercollection/daily_readiness",
            {"start_date": self.yesterday_str, "end_date": self.today_str}
        )
        if readiness and "data" in readiness and readiness["data"]:
            self.health_data["readiness"] = readiness["data"][-1]

        # 睡眠数据
        sleep = self.make_request(
            "usercollection/daily_sleep",
            {"start_date": self.yesterday_str, "end_date": self.today_str}
        )
        if sleep and "data" in sleep and sleep["data"]:
            self.health_data["sleep"] = sleep["data"][-1]

        # 活动数据
        activity = self.make_request(
            "usercollection/daily_activity",
            {"start_date": self.yesterday_str, "end_date": self.today_str}
        )
        if activity and "data" in activity and activity["data"]:
            self.health_data["activity"] = activity["data"][-1]

        print("✓ Oura Ring数据获取完成")

    def get_weather_data(self):
        """获取天气数据"""
        print(f"🌤️ 获取{CITY}天气数据...")

        try:
            # 使用wttr.in获取天气数据（免费，无需API key）
            url = f"https://wttr.in/{CITY}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 提取当前天气
            current = data.get("current_condition", [{}])[0]

            # 提取今日预报
            today_forecast = None
            for day in data.get("weather", []):
                if day.get("date") == self.today.strftime("%Y-%m-%d"):
                    today_forecast = day
                    break

            self.weather_data = {
                "city": CITY,
                "current": {
                    "temp_c": int(current.get("temp_C", 0)),
                    "feels_like_c": int(current.get("FeelsLikeC", 0)),
                    "humidity": int(current.get("humidity", 0)),
                    "wind_speed_kmh": int(current.get("windspeedKmph", 0)),
                    "weather_desc": current.get("weatherDesc", [{}])[0].get("value", ""),
                    "uv_index": int(current.get("uvIndex", 0))
                },
                "forecast": {
                    "max_temp_c": int(today_forecast.get("maxtempC", 0)) if today_forecast else 0,
                    "min_temp_c": int(today_forecast.get("mintempC", 0)) if today_forecast else 0,
                    "avg_temp_c": int(today_forecast.get("avgtempC", 0)) if today_forecast else 0,
                    "total_precip_mm": float(today_forecast.get("totalprecip_mm", 0)) if today_forecast else 0,
                    "chance_of_rain": int(today_forecast.get("chanceofrain", 0)) if today_forecast else 0,
                    "sunrise": today_forecast.get("astronomy", [{}])[0].get("sunrise", "") if today_forecast else "",
                    "sunset": today_forecast.get("astronomy", [{}])[0].get("sunset", "") if today_forecast else ""
                } if today_forecast else {}
            }

            print(f"✓ 天气数据获取完成: {self.weather_data['current']['temp_c']}°C")

        except Exception as e:
            print(f"⚠️ 天气数据获取失败: {e}")
            self.weather_data = {}

    def get_aqi_data(self):
        """获取空气质量数据"""
        print(f"🌬️ 获取{CITY}空气质量数据...")

        try:
            # 使用waqi.info获取空气质量（免费，无需API key）
            url = f"https://api.waqi.info/feed/{CITY}/?token="
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ok":
                iaqi = data.get("data", {}).get("iaqi", {})

                self.aqi_data = {
                    "aqi": int(data.get("data", {}).get("aqi", 0)),
                    "pm25": int(iaqi.get("pm25", {}).get("v", 0)),
                    "pm10": int(iaqi.get("pm10", {}).get("v", 0)),
                    "o3": int(iaqi.get("o3", {}).get("v", 0)),
                    "no2": int(iaqi.get("no2", {}).get("v", 0)),
                    "so2": int(iaqi.get("so2", {}).get("v", 0)),
                    "city": data.get("data", {}).get("city", {}).get("name", CITY)
                }

                print(f"✓ 空气质量获取完成: AQI {self.aqi_data['aqi']}")
            else:
                self.aqi_data = {}

        except Exception as e:
            print(f"⚠️ 空气质量获取失败: {e}")
            self.aqi_data = {}

    def get_clothing_advice(self):
        """根据天气生成穿着建议"""
        if not self.weather_data:
            return "天气数据暂无"

        temp = self.weather_data["current"]["temp_c"]
        feels_like = self.weather_data["current"]["feels_like_c"]
        humidity = self.weather_data["current"]["humidity"]
        weather_desc = self.weather_data["current"]["weather_desc"]
        wind_speed = self.weather_data["current"]["wind_speed_kmh"]
        rain_chance = self.weather_data["forecast"].get("chance_of_rain", 0)

        advice = []

        # 温度建议
        if temp <= 5:
            advice.append("🧥 寒冷：羽绒服、厚毛衣、保暖内衣")
        elif temp <= 15:
            advice.append("🧥 较冷：夹克、毛衣、长裤")
        elif temp <= 22:
            advice.append("👕 适中：长袖衬衫、薄外套")
        elif temp <= 28:
            advice.append("👕 舒适：短袖、轻薄衣物")
        else:
            advice.append("🩳 炎热：短袖、短裤、透气衣物")

        # 体感温度调整
        if abs(feels_like - temp) > 3:
            if feels_like < temp:
                advice.append(f"❄️ 体感更冷({feels_like}°C)，建议多穿一层")
            else:
                advice.append(f"☀️ 体感更热({feels_like}°C)，建议穿少一点")

        # 湿度建议
        if humidity > 80:
            advice.append("💧 湿度较高，选择透气、速干衣物")

        # 风速建议
        if wind_speed > 20:
            advice.append("💨 风较大，建议穿防风外套")

        # 雨天建议
        if rain_chance > 50:
            advice.append(f"☔ 降雨概率{rain_chance}%，携带雨具")
        elif "rain" in weather_desc.lower():
            advice.append("☔ 今日有雨，携带雨具")

        # 户外运动建议
        if temp >= 15 and temp <= 25 and rain_chance < 30:
            advice.append("🏃 天气适宜，适合户外训练")
        elif temp < 5 or temp > 30:
            advice.append("🏠 建议室内训练")

        return "\n".join(advice)

    def get_aqi_advice(self):
        """根据空气质量生成建议"""
        if not self.aqi_data:
            return "空气质量数据暂无"

        aqi = self.aqi_data["aqi"]
        pm25 = self.aqi_data["pm25"]

        advice = []

        # AQI等级和建议
        if aqi <= 50:
            advice.append("🟢 空气质量优")
            advice.append("✓ 适合户外活动")
            advice.append("✓ 适合高强度训练")
        elif aqi <= 100:
            advice.append("🟡 空气质量良")
            advice.append("✓ 可以户外活动")
            advice.append("✓ 敏感人群减少长时间高强度运动")
        elif aqi <= 150:
            advice.append("🟠 空气质量轻度污染")
            advice.append("⚠️ 减少户外活动时间")
            advice.append("⚠️ 建议室内训练")
            advice.append("⚠️ 避免长时间高强度户外运动")
        elif aqi <= 200:
            advice.append("🔴 空气质量中度污染")
            advice.append("❌ 避免户外运动")
            advice.append("✓ 建议室内训练")
            advice.append("⚠️ 外出佩戴防护口罩")
        else:
            advice.append("🟣 空气质量重度污染")
            advice.append("❌ 避免所有户外活动")
            advice.append("❌ 避免开窗通风")
            advice.append("⚠️ 使用空气净化器")
            advice.append("⚠️ 必须外出时佩戴N95口罩")

        # PM2.5建议
        if pm25 > 75:
            advice.append(f"⚠️ PM2.5浓度较高({pm25} μg/m³)，对肺部有压力")
            advice.append("⚠️ 自由潜水需特别注意，避免高强度呼吸训练")

        return "\n".join(advice)

    def get_training_recommendation(self):
        """生成综合训练建议"""
        recommendations = []

        # 基于准备度
        readiness_score = self.health_data.get("readiness", {}).get("score", 0)
        hrv_balance = self.health_data.get("readiness", {}).get("contributors", {}).get("hrv_balance", 0)
        recovery_index = self.health_data.get("readiness", {}).get("contributors", {}).get("recovery_index", 0)

        if readiness_score >= 85:
            recommendations.append({
                "level": "⭐ 高强度",
                "icon": "🔥",
                "training": "可以进行高强度闭气训练、深度挑战、技术精练",
                "readiness": f"准备度 {readiness_score}/100 - 状态优秀"
            })
        elif readiness_score >= 70:
            recommendations.append({
                "level": "✓ 中等强度",
                "icon": "💪",
                "training": "适合中等强度训练，注意监测身体反应",
                "readiness": f"准备度 {readiness_score}/100 - 状态良好"
            })
        elif readiness_score >= 55:
            recommendations.append({
                "level": "⚠️ 低强度",
                "icon": "🚶",
                "training": "建议轻度训练或休息，优先恢复",
                "readiness": f"准备度 {readiness_score}/100 - 状态一般"
            })
        else:
            recommendations.append({
                "level": "❌ 休息",
                "icon": "🛌",
                "training": "建议完全休息，避免高强度训练",
                "readiness": f"准备度 {readiness_score}/100 - 状态不佳"
            })

        # HRV建议
        if hrv_balance < 60:
            recommendations.append({
                "level": "⚠️ 注意疲劳",
                "icon": "😔",
                "advice": f"HRV平衡 {hrv_balance}/100 偏低，可能存在疲劳累积",
                "action": "建议减少训练强度，增加休息时间"
            })
        elif hrv_balance >= 85:
            recommendations.append({
                "level": "✓ 恢复良好",
                "icon": "😊",
                "advice": f"HRV平衡 {hrv_balance}/100 优秀，自主神经系统恢复良好",
                "action": "适合训练"
            })

        # 恢复指数
        if recovery_index < 50:
            recommendations.append({
                "level": "⚠️ 恢复不足",
                "icon": "🔋",
                "advice": f"恢复指数 {recovery_index}/100 偏低",
                "action": "注意休息和睡眠质量"
            })

        # 结合天气
        if self.weather_data:
            temp = self.weather_data["current"]["temp_c"]
            rain_chance = self.weather_data["forecast"].get("chance_of_rain", 0)

            if temp < 10 or temp > 32:
                recommendations.append({
                    "level": "🏠 室内训练建议",
                    "icon": "🏋️",
                    "advice": f"当前温度{temp}°C，不适宜户外训练",
                    "action": "建议在健身房或室内泳池训练"
                })

            if rain_chance > 70:
                recommendations.append({
                    "level": "☔ 雨天建议",
                    "icon": "🌧️",
                    "advice": f"降雨概率{rain_chance}%",
                    "action": "建议室内训练或调整训练时间"
                })

        # 结合空气质量
        if self.aqi_data:
            aqi = self.aqi_data["aqi"]
            if aqi > 100:
                recommendations.append({
                    "level": "🌬️ 空气质量建议",
                    "icon": "😷",
                    "advice": f"AQI {aqi}，不适宜户外训练",
                    "action": "建议室内训练，避免户外有氧运动"
                })

        return recommendations

    def get_supplement_reminder(self):
        """生成补剂提醒"""
        day_of_month = self.today.day

        reminder = {
            "medication": {
                "name": "异维A酸",
                "dose": "10mg",
                "is_medication_day": day_of_month % 2 == 0,
                "note": "隔日疗法（偶数日服用）"
            },
            "daily_supplements": [
                {"name": "NMN22000", "dose": "1粒", "time": "早晨"},
                {"name": "益生菌", "dose": "1粒", "time": "空腹/早餐前"},
                {"name": "鱼油 (Omega-3)", "dose": "按说明", "time": "早餐后"},
                {"name": "维生素D3", "dose": "按说明", "time": "午餐后"},
                {"name": "镁", "dose": "按说明", "time": "睡前"}
            ],
            "conditional_supplements": []
        }

        # 训练日补剂
        activity_score = self.health_data.get("activity", {}).get("score", 0)
        if activity_score > 0:
            reminder["conditional_supplements"].append({
                "name": "肌酸",
                "dose": "3g",
                "time": "训练前30分钟",
                "condition": "训练日"
            })

        return reminder

    def generate_html_dashboard(self):
        """生成HTML格式的看板"""
        html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金明 - 健康看板</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 14px;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .card h2 {{
            color: #333;
            font-size: 18px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .score-display {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
        }}

        .score {{
            font-size: 48px;
            font-weight: bold;
        }}

        .score.excellent {{ color: #10b981; }}
        .score.good {{ color: #3b82f6; }}
        .score.fair {{ color: #f59e0b; }}
        .score.poor {{ color: #ef4444; }}

        .score-label {{
            color: #666;
            font-size: 14px;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}

        .metric {{
            background: #f9fafb;
            padding: 10px;
            border-radius: 8px;
        }}

        .metric-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}

        .metric-value {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }}

        .weather-display {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 15px;
        }}

        .temp {{
            font-size: 48px;
            font-weight: bold;
            color: #333;
        }}

        .weather-icon {{
            font-size: 48px;
        }}

        .advice-list {{
            list-style: none;
        }}

        .advice-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}

        .advice-list li:last-child {{
            border-bottom: none;
        }}

        .aqi-display {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }}

        .aqi {{
            font-size: 48px;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 10px;
            color: white;
        }}

        .aqi.good {{ background: #10b981; }}
        .aqi.moderate {{ background: #f59e0b; }}
        .aqi.unhealthy {{ background: #ef4444; }}
        .aqi.hazardous {{ background: #8b5cf6; }}

        .recommendation {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }}

        .recommendation-header {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }}

        .supplement-list {{
            list-style: none;
        }}

        .supplement-list li {{
            padding: 10px;
            background: #f9fafb;
            margin-bottom: 8px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .supplement-list li.medication-day {{
            background: #dbeafe;
            border-left: 4px solid #3b82f6;
        }}

        .supplement-list li.no-medication {{
            background: #f3f4f6;
            border-left: 4px solid #9ca3af;
        }}

        .checkbox {{
            width: 20px;
            height: 20px;
            border: 2px solid #667eea;
            border-radius: 4px;
            margin-right: 10px;
            flex-shrink: 0;
        }}

        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏊 金明 - 健康看板</h1>
            <div class="subtitle">
                <span id="date"></span> | 自由潜水世界纪录保持者
            </div>
        </div>

        <div class="grid">
            <!-- 准备度 -->
            <div class="card">
                <h2>📊 准备度</h2>
                <div class="score-display">
                    <div class="score {score_class}" id="readiness-score">-</div>
                    <div class="score-label">今日准备度</div>
                </div>
                <div class="metric-grid" id="readiness-metrics"></div>
            </div>

            <!-- 睡眠 -->
            <div class="card">
                <h2>😴 睡眠质量</h2>
                <div class="score-display">
                    <div class="score {sleep_class}" id="sleep-score">-</div>
                    <div class="score-label">睡眠评分</div>
                </div>
                <div class="metric-grid" id="sleep-metrics"></div>
            </div>

            <!-- 活动 -->
            <div class="card">
                <h2>🏃 活动数据</h2>
                <div class="score-display">
                    <div class="score {activity_class}" id="activity-score">-</div>
                    <div class="score-label">活动评分</div>
                </div>
                <div class="metric-grid" id="activity-metrics"></div>
            </div>

            <!-- 天气 -->
            <div class="card">
                <h2>🌤️ 天气信息</h2>
                <div class="weather-display" id="weather-display"></div>
                <div class="metric-grid" id="weather-metrics"></div>
            </div>

            <!-- 空气质量 -->
            <div class="card">
                <h2>🌬️ 空气质量</h2>
                <div class="aqi-display" id="aqi-display"></div>
                <div class="metric-grid" id="aqi-metrics"></div>
            </div>

            <!-- 穿着建议 -->
            <div class="card">
                <h2>👔 穿着建议</h2>
                <ul class="advice-list" id="clothing-advice"></ul>
            </div>

            <!-- 训练建议 -->
            <div class="card" style="grid-column: span 2;">
                <h2>🎯 训练建议</h2>
                <div id="training-recommendations"></div>
            </div>

            <!-- 补剂提醒 -->
            <div class="card" style="grid-column: span 2;">
                <h2>💊 补剂提醒</h2>
                <ul class="supplement-list" id="supplement-list"></ul>
            </div>
        </div>

        <div class="footer">
            <p>数据来源: Oura Ring Gen 3 | 更新时间: <span id="update-time"></span></p>
            <p>如需查看详细数据，请检查 DailyReports 目录</p>
        </div>
    </div>

    <script>
        const healthData = {health_data_json};
        const weatherData = {weather_data_json};
        const aqiData = {aqi_data_json};

        // 更新日期
        document.getElementById('date').textContent = '{today_str}';
        document.getElementById('update-time').textContent = new Date().toLocaleString('zh-CN');

        // 准备度
        if (healthData.readiness) {{
            const readiness = healthData.readiness.score;
            document.getElementById('readiness-score').textContent = readiness;
            document.getElementById('readiness-score').className = 'score ' + (readiness >= 85 ? 'excellent' : readiness >= 70 ? 'good' : readiness >= 55 ? 'fair' : 'poor');

            const metrics = healthData.readiness.contributors || {{}};
            document.getElementById('readiness-metrics').innerHTML = `
                <div class="metric">
                    <div class="metric-label">HRV平衡</div>
                    <div class="metric-value">${{metrics.hrv_balance || 0}}/100</div>
                </div>
                <div class="metric">
                    <div class="metric-label">恢复指数</div>
                    <div class="metric-value">${{metrics.recovery_index || 0}}/100</div>
                </div>
                <div class="metric">
                    <div class="metric-label">静息心率</div>
                    <div class="metric-value">${{metrics.resting_heart_rate || 0}}/100</div>
                </div>
                <div class="metric">
                    <div class="metric-label">睡眠平衡</div>
                    <div class="metric-value">${{metrics.sleep_balance || 0}}/100</div>
                </div>
            `;
        }}

        // 睡眠
        if (healthData.sleep) {{
            const sleep = healthData.sleep.score;
            document.getElementById('sleep-score').textContent = sleep;
            document.getElementById('sleep-score').className = 'score ' + (sleep >= 85 ? 'excellent' : sleep >= 70 ? 'good' : sleep >= 55 ? 'fair' : 'poor');

            const totalHours = (healthData.sleep.total_sleep_duration || 0) / 3600;
            const deepHours = (healthData.sleep.total_deep || 0) / 3600;
            const remHours = (healthData.sleep.total_rem || 0) / 3600;

            document.getElementById('sleep-metrics').innerHTML = `
                <div class="metric">
                    <div class="metric-label">总睡眠</div>
                    <div class="metric-value">${{totalHours.toFixed(1)}}h</div>
                </div>
                <div class="metric">
                    <div class="metric-label">深度睡眠</div>
                    <div class="metric-value">${{deepHours.toFixed(1)}}h</div>
                </div>
                <div class="metric">
                    <div class="metric-label">REM</div>
                    <div class="metric-value">${{remHours.toFixed(1)}}h</div>
                </div>
                <div class="metric">
                    <div class="metric-label">睡眠效率</div>
                    <div class="metric-value">${{healthData.sleep.sleep_efficiency || 0}}%</div>
                </div>
            `;
        }}

        // 活动
        if (healthData.activity) {{
            const activity = healthData.activity.score;
            document.getElementById('activity-score').textContent = activity;
            document.getElementById('activity-score').className = 'score ' + (activity >= 85 ? 'excellent' : activity >= 70 ? 'good' : activity >= 55 ? 'fair' : 'poor');

            document.getElementById('activity-metrics').innerHTML = `
                <div class="metric">
                    <div class="metric-label">步数</div>
                    <div class="metric-value">${{(healthData.activity.steps || 0).toLocaleString()}}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">总消耗</div>
                    <div class="metric-value">${{Math.round(healthData.activity.total_calories || 0)}} kcal</div>
                </div>
                <div class="metric">
                    <div class="metric-label">活动消耗</div>
                    <div class="metric-value">${{Math.round(healthData.activity.active_calories || 0)}} kcal</div>
                </div>
                <div class="metric">
                    <div class="metric-label">距离</div>
                    <div class="metric-value">${{(healthData.activity.distance_km || 0).toFixed(2)}} km</div>
                </div>
            `;
        }}

        // 天气
        if (weatherData.current) {{
            const weatherIcons = {{
                'Sunny': '☀️', 'Clear': '🌙', 'Partly cloudy': '⛅',
                'Cloudy': '☁️', 'Rain': '🌧️', 'Drizzle': '🌦️',
                'Thunderstorm': '⛈️', 'Snow': '❄️', 'Mist': '🌫️'
            }};

            document.getElementById('weather-display').innerHTML = `
                <div class="weather-icon">${{weatherIcons[weatherData.current.weather_desc] || '🌤️'}}</div>
                <div class="temp">${{weatherData.current.temp_c}}°C</div>
            `;

            document.getElementById('weather-metrics').innerHTML = `
                <div class="metric">
                    <div class="metric-label">体感温度</div>
                    <div class="metric-value">${{weatherData.current.feels_like_c}}°C</div>
                </div>
                <div class="metric">
                    <div class="metric-label">湿度</div>
                    <div class="metric-value">${{weatherData.current.humidity}}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">风速</div>
                    <div class="metric-value">${{weatherData.current.wind_speed_kmh}} km/h</div>
                </div>
                <div class="metric">
                    <div class="metric-label">紫外线</div>
                    <div class="metric-value">UV ${{weatherData.current.uv_index}}</div>
                </div>
            `;
        }}

        // 空气质量
        if (aqiData.aqi) {{
            const aqi = aqiData.aqi;
            const aqiClass = aqi <= 50 ? 'good' : aqi <= 100 ? 'moderate' : aqi <= 150 ? 'unhealthy' : 'hazardous';
            document.getElementById('aqi-display').innerHTML = `
                <div class="aqi ${{aqiClass}}">${{aqi}}</div>
                <div>
                    <div style="font-weight: 600;">空气质量指数</div>
                    <div style="font-size: 12px; color: #666;">AQI</div>
                </div>
            `;

            document.getElementById('aqi-metrics').innerHTML = `
                <div class="metric">
                    <div class="metric-label">PM2.5</div>
                    <div class="metric-value">${{aqiData.pm25}} μg/m³</div>
                </div>
                <div class="metric">
                    <div class="metric-label">PM10</div>
                    <div class="metric-value">${{aqiData.pm10}} μg/m³</div>
                </div>
                <div class="metric">
                    <div class="metric-label">O₃</div>
                    <div class="metric-value">${{aqiData.o3}} μg/m³</div>
                </div>
                <div class="metric">
                    <div class="metric-label">NO₂</div>
                    <div class="metric-value">${{aqiData.no2}} μg/m³</div>
                </div>
            `;
        }}
    </script>
</body>
</html>"""

        # 替换数据
        html = html_template.format(
            today_str=self.today_str,
            health_data_json=json.dumps(self.health_data),
            weather_data_json=json.dumps(self.weather_data),
            aqi_data_json=json.dumps(self.aqi_data),
            score_class="",  # 会在JS中动态设置
            sleep_class="",
            activity_class=""
        )

        return html

    def generate_markdown_dashboard(self):
        """生成Markdown格式的看板"""
        md = f"""# 金明 - 全面健康看板

**日期：** {self.today_str}
**生成时间：** {self.today.strftime('%Y-%m-%d %H:%M:%S')}
**用户：** 自由潜水世界纪录保持者

---

## 📊 今日健康评分

### 准备度 (Readiness)
"""

        # 准备度
        if self.health_data.get("readiness"):
            readiness = self.health_data["readiness"]
            score = readiness.get("score", 0)
            emoji = "⭐" if score >= 85 else "✓" if score >= 70 else "⚠️"
            status = "优秀" if score >= 85 else "良好" if score >= 70 else "一般" if score >= 55 else "不佳"

            md += f"""
**分数：** {score}/100 {emoji} ({status})

| 指标 | 数值 | 评价 |
|------|------|------|
| HRV平衡 | {readiness.get('contributors', {}).get('hrv_balance', 0)}/100 | {'✓' if readiness.get('contributors', {}).get('hrv_balance', 0) >= 75 else '⚠️'} |
| 恢复指数 | {readiness.get('contributors', {}).get('recovery_index', 0)}/100 | {'✓' if readiness.get('contributors', {}).get('recovery_index', 0) >= 75 else '⚠️'} |
| 静息心率 | {readiness.get('contributors', {}).get('resting_heart_rate', 0)}/100 | - |
| 睡眠平衡 | {readiness.get('contributors', {}).get('sleep_balance', 0)}/100 | {'✓' if readiness.get('contributors', {}).get('sleep_balance', 0) >= 75 else '⚠️'} |
| 活动平衡 | {readiness.get('contributors', {}).get('activity_balance', 0)}/100 | - |
"""
        else:
            md += "\n⚠️ 今日暂无准备度数据\n\n"

        # 睡眠
        md += "\n### 😴 睡眠质量\n\n"

        if self.health_data.get("sleep"):
            sleep = self.health_data["sleep"]
            score = sleep.get("score", 0)
            total_hours = sleep.get("total_sleep_duration", 0) / 3600
            deep_hours = sleep.get("total_deep", 0) / 3600
            rem_hours = sleep.get("total_rem", 0) / 3600

            md += f"""**分数：** {score}/100

| 指标 | 数值 |
|------|------|
| 总睡眠时长 | {total_hours:.1f} 小时 |
| 深度睡眠 | {deep_hours:.1f} 小时 ({deep_hours/total_hours*100 if total_hours > 0 else 0:.1f}%) |
| 快速眼动睡眠 | {rem_hours:.1f} 小时 ({rem_hours/total_hours*100 if total_hours > 0 else 0:.1f}%) |
| 睡眠效率 | {sleep.get('sleep_efficiency', 0):.1f}% |
| 入睡时间 | {sleep.get('onset_latency', 0)/60:.1f} 分钟 |
| 平均心率 | {sleep.get('average_hr', 0):.0f} bpm |
| 最低心率 | {sleep.get('lowest_hr', 0):.0f} bpm |
| 平均HRV | {sleep.get('average_hrv', 0):.0f} ms |
"""
        else:
            md += "⚠️ 昨晚暂无睡眠数据\n\n"

        # 活动
        md += "\n### 🏃 活动数据\n\n"

        if self.health_data.get("activity"):
            activity = self.health_data["activity"]

            md += f"""**分数：** {activity.get('score', 0)}/100

| 指标 | 数值 |
|------|------|
| 步数 | {activity.get('steps', 0):,} 步 |
| 总消耗 | {activity.get('total_calories', 0):.0f} 千卡 |
| 活动消耗 | {activity.get('active_calories', 0):.0f} 千卡 |
| 距离 | {activity.get('distance_km', 0):.2f} 公里 |
| 等效步行距离 | {activity.get('equivalent_walking_distance_km', 0):.2f} 公里 |
"""
        else:
            md += "⚠️ 今日暂无活动数据\n\n"

        # 天气信息
        md += "\n---\n\n## 🌤️ 天气信息\n\n"

        if self.weather_data.get("current"):
            current = self.weather_data["current"]
            forecast = self.weather_data.get("forecast", {})

            md += f"""### 当前天气

**{CITY}** | {current.get('weather_desc', '')}

| 指标 | 数值 |
|------|------|
| 温度 | {current.get('temp_c', 0)}°C |
| 体感温度 | {current.get('feels_like_c', 0)}°C |
| 湿度 | {current.get('humidity', 0)}% |
| 风速 | {current.get('wind_speed_kmh', 0)} km/h |
| 紫外线指数 | UV {current.get('uv_index', 0)} |

### 今日预报

| 指标 | 数值 |
|------|------|
| 最高温度 | {forecast.get('max_temp_c', 0)}°C |
| 最低温度 | {forecast.get('min_temp_c', 0)}°C |
| 平均温度 | {forecast.get('avg_temp_c', 0)}°C |
| 降水量 | {forecast.get('total_precip_mm', 0)} mm |
| 降雨概率 | {forecast.get('chance_of_rain', 0)}% |
| 日出 | {forecast.get('sunrise', '')} |
| 日落 | {forecast.get('sunset', '')} |

"""
        else:
            md += "⚠️ 天气数据暂无\n\n"

        # 穿着建议
        md += "### 👔 穿着建议\n\n"
        md += self.get_clothing_advice() + "\n\n"

        # 空气质量
        md += "\n---\n\n## 🌬️ 空气质量\n\n"

        if self.aqi_data.get("aqi"):
            aqi = self.aqi_data["aqi"]

            md += f"""### AQI 指数：**{aqi}** {'🟢 优' if aqi <= 50 else '🟡 良' if aqi <= 100 else '🟠 轻度污染' if aqi <= 150 else '🔴 中度污染' if aqi <= 200 else '🟣 重度污染'}

| 指标 | 数值 |
|------|------|
| PM2.5 | {self.aqi_data.get('pm25', 0)} μg/m³ |
| PM10 | {self.aqi_data.get('pm10', 0)} μg/m³ |
| 臭氧 (O₃) | {self.aqi_data.get('o3', 0)} μg/m³ |
| 二氧化氮 (NO₂) | {self.aqi_data.get('no2', 0)} μg/m³ |
| 二氧化硫 (SO₂) | {self.aqi_data.get('so2', 0)} μg/m³ |

### 空气质量建议

{self.get_aqi_advice()}

"""
        else:
            md += "⚠️ 空气质量数据暂无\n\n"

        # 训练建议
        md += "\n---\n\n## 🎯 训练建议\n\n"

        recommendations = self.get_training_recommendation()

        for i, rec in enumerate(recommendations, 1):
            md += f"### {rec.get('icon', '')} {rec.get('level', '')}\n\n"
            for key, value in rec.items():
                if key not in ["icon", "level"]:
                    md += f"**{key}：** {value}\n\n"

        # 补剂提醒
        md += "\n---\n\n## 💊 补剂提醒\n\n"

        supplement = self.get_supplement_reminder()
        medication = supplement["medication"]

        if medication["is_medication_day"]:
            md += f"### 今日服药日 ✓\n\n"
            md += f"- ☑ **{medication['name']}** {medication['dose']} - {medication['note']}\n\n"
        else:
            md += f"### 今日非服药日 ○\n\n"
            md += f"- ☐ **{medication['name']}** {medication['dose']} - {medication['note']}\n\n"

        md += "### 日常补剂\n\n"
        for supp in supplement["daily_supplements"]:
            md += f"- ☑ **{supp['name']}** - {supp['dose']} ({supp['time']})\n"

        if supplement["conditional_supplements"]:
            md += "\n### 训练日补剂\n\n"
            for supp in supplement["conditional_supplements"]:
                md += f"- ☑ **{supp['name']}** - {supp['dose']} ({supp['condition']})\n"

        # 数据文件位置
        md += f"""

---

## 📋 数据文件位置

- **HTML看板：** `DailyReports/dashboard_{self.today_str}.html`
- **Markdown报告：** `DailyReports/dashboard_{self.today_str}.md`
- **JSON数据：** `DailyReports/dashboard_{self.today_str}.json`

---

*报告生成时间：{self.today.strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源：Oura Ring Gen 3 + 天气API + 空气质量API*
"""

        return md

    def generate(self):
        """生成所有格式的报告"""
        print("=" * 60)
        print("金明 - 全面健康报告看板")
        print("=" * 60)

        # 获取所有数据
        self.get_oura_data()
        self.get_weather_data()
        self.get_aqi_data()

        # 生成HTML看板
        html_content = self.generate_html_dashboard()
        html_file = self.dashboard_dir / f"dashboard_{self.today_str}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n✓ HTML看板已保存: {html_file}")

        # 生成Markdown报告
        md_content = self.generate_markdown_dashboard()
        md_file = self.dashboard_dir / f"dashboard_{self.today_str}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"✓ Markdown报告已保存: {md_file}")

        # 保存JSON数据
        all_data = {
            "date": self.today_str,
            "generated_at": self.today.isoformat(),
            "health": self.health_data,
            "weather": self.weather_data,
            "aqi": self.aqi_data
        }
        json_file = self.dashboard_dir / f"dashboard_{self.today_str}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON数据已保存: {json_file}")

        print("\n" + "=" * 60)
        print("✓ 全面健康看板生成完成！")
        print("=" * 60)
        print(f"\n在浏览器中打开查看：")
        print(f"file://{html_file.absolute()}")

def main():
    """主函数"""
    dashboard = ComprehensiveHealthDashboard()
    dashboard.generate()

if __name__ == "__main__":
    main()
