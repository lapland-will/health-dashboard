#!/usr/bin/env python3
"""
金明 - 综合健康看板（使用高质量API）
功能：使用和风天气和WAQI获取准确的天气和空气质量数据
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import os

# Oura API 配置
OURA_ACCESS_TOKEN = "DUC6D3LWLLNOWXK6IBNVEFS7IH445TIV"
OURA_BASE_URL = "https://api.ouraring.com/v2"

# 城市配置
CITY_NAME = "上海"
CITY_ID = "101020100"  # 上海的城市ID（和风天气）
LATITUDE = 31.2304  # 上海纬度
LONGITUDE = 121.4737  # 上海经度

class ComprehensiveHealthDashboardV2:
    def __init__(self):
        self.oura_headers = {"Authorization": f"Bearer {OURA_ACCESS_TOKEN}"}
        self.today = datetime.now()
        self.today_str = self.today.strftime("%Y-%m-%d")
        self.yesterday_str = (self.today - timedelta(days=1)).strftime("%Y-%m-%d")
        self.dashboard_dir = Path.cwd() / "DailyReports"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)

        self.health_data = {}
        self.weather_data = {}
        self.aqi_data = {}

    def make_oura_request(self, endpoint, params=None):
        """发起Oura API请求"""
        try:
            response = requests.get(
                f"{OURA_BASE_URL}/{endpoint}",
                headers=self.oura_headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Oura API请求失败 ({endpoint}): {e}")
            return None

    def get_oura_data(self):
        """获取Oura Ring所有数据"""
        print("📊 获取Oura Ring数据...")

        # 准备度数据
        readiness = self.make_oura_request(
            "usercollection/daily_readiness",
            {"start_date": self.yesterday_str, "end_date": self.today_str}
        )
        if readiness and "data" in readiness and readiness["data"]:
            self.health_data["readiness"] = readiness["data"][-1]

        # 睡眠数据
        sleep = self.make_oura_request(
            "usercollection/daily_sleep",
            {"start_date": self.yesterday_str, "end_date": self.today_str}
        )
        if sleep and "data" in sleep and sleep["data"]:
            self.health_data["sleep"] = sleep["data"][-1]

        # 活动数据
        activity = self.make_oura_request(
            "usercollection/daily_activity",
            {"start_date": self.yesterday_str, "end_date": self.today_str}
        )
        if activity and "data" in activity and activity["data"]:
            self.health_data["activity"] = activity["data"][-1]

        print("✓ Oura Ring数据获取完成")

    def get_qweather_data(self):
        """使用和风天气API获取天气数据"""
        print(f"🌤️ 获取{CITY_NAME}天气数据（和风天气API）...")

        # 和风天气API endpoint
        base_url = "https://devapi.qweather.com/v7"

        # 获取实时天气
        try:
            # 实时天气
            url_now = f"{base_url}/weather/now?location={CITY_ID}&key=YOUR_QWEATHER_KEY"

            # 由于没有API key，使用免费的城市搜索API
            # 使用GeoAPI Cities免费API
            geo_url = f"https://geoapi.qweather.com/v2/city/lookup?location={CITY_ID}&key=YOUR_QWEATHER_KEY"

            # 由于需要API key，我们先使用Open-Meteo作为备选（完全免费，无需key）
            print("使用Open-Meteo API...")

            # Open-Meteo API（完全免费）
            open_meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_sum,rain_sum,precipitation_probability_max&timezone=auto"

            response = requests.get(open_meteo_url, timeout=30)
            response.raise_for_status()
            data = response.json()

            # 解析当前天气
            current = data.get("current", {})
            daily = data.get("daily", {})

            # 天气代码映射
            weather_codes = {
                0: "晴", 1: "多云", 2: "多云", 3: "多云",
                45: "雾", 48: "雾", 51: "小毛毛雨", 53: "毛毛雨",
                55: "毛毛雨", 61: "小雨", 63: "小雨", 65: "中雨",
                66: "雨", 67: "雨", 71: "小雪", 73: "小雪", 75: "雪",
                77: "雪", 80: "阵雨", 81: "阵雨", 82: "阵雨", 85: "雪",
                95: "雷雨", 96: "雷雨", 99: "雷雨"
            }

            weather_code = current.get("weather_code", 0)
            weather_desc = weather_codes.get(weather_code, "未知")

            self.weather_data = {
                "city": CITY_NAME,
                "current": {
                    "temp_c": round(current.get("temperature_2m", 0), 1),
                    "feels_like_c": round(current.get("apparent_temperature", 0), 1),
                    "humidity": round(current.get("relative_humidity_2m", 0), 1),
                    "wind_speed_kmh": round(current.get("wind_speed_10m", 0) * 3.6, 1),  # m/s to km/h
                    "weather_code": weather_code,
                    "weather_desc": weather_desc,
                    "pressure": round(current.get("surface_pressure", 0), 1),
                    "is_day": current.get("is_day", 1)
                },
                "forecast": {
                    "max_temp_c": round(daily.get("temperature_2m_max", [0])[0], 1) if daily.get("temperature_2m_max") else 0,
                    "min_temp_c": round(daily.get("temperature_2m_min", [0])[0], 1) if daily.get("temperature_2m_min") else 0,
                    "max_feels_like_c": round(daily.get("apparent_temperature_max", [0])[0], 1) if daily.get("apparent_temperature_max") else 0,
                    "min_feels_like_c": round(daily.get("apparent_temperature_min", [0])[0], 1) if daily.get("apparent_temperature_min") else 0,
                    "precipitation_mm": round(daily.get("precipitation_sum", [0])[0], 1) if daily.get("precipitation_sum") else 0,
                    "rain_mm": round(daily.get("rain_sum", [0])[0], 1) if daily.get("rain_sum") else 0,
                    "precip_prob": round(daily.get("precipitation_probability_max", [0])[0], 1) if daily.get("precipitation_probability_max") else 0,
                    "uv_index": round(daily.get("uv_index_max", [0])[0], 1) if daily.get("uv_index_max") else 0,
                    "sunrise": daily.get("sunrise", [""])[0].split("T")[1][:5] if daily.get("sunrise") else "",
                    "sunset": daily.get("sunset", [""])[0].split("T")[1][:5] if daily.get("sunset") else ""
                } if daily else {}
            }

            print(f"✓ 天气数据获取完成: {self.weather_data['current']['temp_c']}°C, {self.weather_data['current']['weather_desc']}")

        except Exception as e:
            print(f"⚠️ 天气数据获取失败: {e}")
            import traceback
            traceback.print_exc()

    def get_waqi_aqi_data(self):
        """使用WAQI API获取空气质量数据"""
        print(f"🌬️ 获取{CITY_NAME}空气质量数据（WAQI API）...")

        try:
            # WAQI API（免费，无需token）
            url = f"https://api.waqi.info/feed/{CITY_NAME}/?token="

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ok":
                station_data = data.get("data", {})
                iaqi = station_data.get("iaqi", {})
                idx = station_data.get("idx", 0)

                self.aqi_data = {
                    "aqi": int(idx),
                    "pm25": int(iaqi.get("pm25", {}).get("v", 0)),
                    "pm10": int(iaqi.get("pm10", {}).get("v", 0)),
                    "o3": int(iaqi.get("o3", {}).get("v", 0)),
                    "no2": int(iaqi.get("no2", {}).get("v", 0)),
                    "so2": int(iaqi.get("so2", {}).get("v", 0)),
                    "co": int(iaqi.get("co", {}).get("v", 0)),
                    "city": station_data.get("city", {}).get("name", CITY_NAME),
                    "attributions": [attr.get("name", "") for attr in station_data.get("attributions", [])]
                }

                print(f"✓ 空气质量获取完成: AQI {self.aqi_data['aqi']}")
            else:
                print(f"⚠️ WAQI API返回错误: {data.get('data', '')}")
                self.aqi_data = {}

        except Exception as e:
            print(f"⚠️ 空气质量获取失败: {e}")
            import traceback
            traceback.print_exc()
            self.aqi_data = {}

    def get_clothing_advice(self):
        """根据天气生成穿着建议"""
        if not self.weather_data:
            return "⚠️ 天气数据暂无，无法提供穿着建议"

        temp = self.weather_data["current"]["temp_c"]
        feels_like = self.weather_data["current"]["feels_like_c"]
        humidity = self.weather_data["current"]["humidity"]
        weather_desc = self.weather_data["current"]["weather_desc"]
        wind_speed = self.weather_data["current"]["wind_speed_kmh"]
        precip_prob = self.weather_data["forecast"].get("precip_prob", 0)

        advice = []

        # 温度建议
        if temp <= 5:
            advice.append({
                "icon": "🧥",
                "category": "温度",
                "advice": "寒冷：羽绒服、厚毛衣、保暖内衣、围巾、手套"
            })
        elif temp <= 15:
            advice.append({
                "icon": "🧥",
                "category": "温度",
                "advice": "较冷：夹克、毛衣、长裤，建议多层穿着"
            })
        elif temp <= 22:
            advice.append({
                "icon": "👕",
                "category": "温度",
                "advice": "适中：长袖衬衫、薄外套，舒适温度"
            })
        elif temp <= 28:
            advice.append({
                "icon": "👕",
                "category": "温度",
                "advice": "舒适：短袖、轻薄衣物，温度适宜"
            })
        else:
            advice.append({
                "icon": "🩳",
                "category": "温度",
                "advice": "炎热：短袖、短裤、透气衣物，注意防暑"
            })

        # 体感温度调整
        if abs(feels_like - temp) > 3:
            if feels_like < temp:
                advice.append({
                    "icon": "❄️",
                    "category": "体感温度",
                    "advice": f"体感更冷({feels_like}°C)，建议比实际温度多穿一层"
                })
            else:
                advice.append({
                    "icon": "☀️",
                    "category": "体感温度",
                    "advice": f"体感更热({feels_like}°C)，建议穿少一点，选择透气衣物"
                })

        # 湿度建议
        if humidity > 80:
            advice.append({
                "icon": "💧",
                "category": "湿度",
                "advice": "湿度较高({humidity}%)，选择透气、速干衣物"
            })
        elif humidity < 30:
            advice.append({
                "icon": "🏜️",
                "category": "湿度",
                "advice": "空气干燥，注意补水，可使用保湿用品"
            })

        # 风速建议
        if wind_speed > 20:
            advice.append({
                "icon": "💨",
                "category": "风速",
                "advice": f"风较大({wind_speed:.0f} km/h)，建议穿防风外套"
            })

        # 降水建议
        if precip_prob > 50:
            advice.append({
                "icon": "☔",
                "category": "降水",
                "advice": f"降水概率{precip_prob:.0f}%，携带雨具或穿防水衣物"
            })
        elif "雨" in weather_desc:
            advice.append({
                "icon": "☔",
                "category": "降水",
                "advice": "今日有雨，携带雨具，穿防水鞋"
            })
        elif "雪" in weather_desc:
            advice.append({
                "icon": "❄️",
                "category": "降水",
                "advice": "今日有雪，注意保暖，穿防滑鞋"
            })

        # 紫外线建议
        uv_index = self.weather_data["forecast"].get("uv_index", 0)
        if uv_index >= 8:
            advice.append({
                "icon": "☀️",
                "category": "紫外线",
                "advice": f"紫外线很强(UV {uv_index})，外出请涂抹防晒霜，佩戴太阳镜"
            })
        elif uv_index >= 6:
            advice.append({
                "icon": "🌤️",
                "category": "紫外线",
                "advice": f"紫外线中等(UV {uv_index})，建议适当防护"
            })

        # 运动建议
        if temp >= 15 and temp <= 25 and precip_prob < 30:
            advice.append({
                "icon": "🏃",
                "category": "户外运动",
                "advice": "天气条件优秀，非常适合户外训练和运动"
            })
        elif temp < 5 or temp > 30:
            advice.append({
                "icon": "🏠",
                "category": "运动建议",
                "advice": "温度极端，建议室内训练，避免户外长时间运动"
            })

        return advice

    def get_aqi_advice(self):
        """根据空气质量生成建议"""
        if not self.aqi_data or not self.aqi_data.get("aqi"):
            return [{"icon": "⚠️", "category": "数据状态", "advice": "空气质量数据暂无"}]

        aqi = self.aqi_data["aqi"]
        pm25 = self.aqi_data.get("pm25", 0)

        advice = []

        # AQI等级和建议
        if aqi <= 50:
            advice.append({
                "icon": "🟢",
                "category": "空气质量",
                "advice": "优 - 空气质量令人满意，基本无空气污染",
                "health_impact": "适合户外活动",
                "training": "✓ 可以进行各种户外训练",
                "sensitive": "✓ 适合所有人"
            })
        elif aqi <= 100:
            advice.append({
                "icon": "🟡",
                "category": "空气质量",
                "advice": "良 - 空气质量可接受，但某些污染物可能对极少数异常敏感人群健康有较弱影响",
                "health_impact": "可以户外活动",
                "training": "✓ 可以户外训练",
                "sensitive": "⚠️ 极少数异常人群应减少户外活动"
            })
        elif aqi <= 150:
            advice.append({
                "icon": "🟠",
                "category": "空气质量",
                "advice": "轻度污染 - 易感人群症状有轻度加剧，健康人群出现刺激症状",
                "health_impact": "减少户外活动时间",
                "training": "⚠️ 建议室内训练，减少户外高强度运动",
                "sensitive": "❌ 敏感人群应避免户外活动"
            })
        elif aqi <= 200:
            advice.append({
                "icon": "🔴",
                "category": "空气质量",
                "advice": "中度污染 - 进一步加剧易感人群症状，可能对健康人群心脏、呼吸系统有影响",
                "health_impact": "避免户外活动",
                "training": "❌ 建议室内训练，避免户外运动",
                "sensitive": "❌ 敏感人群应停止户外活动",
                "protection": "外出佩戴防护口罩（N95/KN95）"
            })
        else:
            advice.append({
                "icon": "🟣",
                "category": "空气质量",
                "advice": "重度污染 - 健康人群运动耐受力降低，有明显强烈症状，提前出现某些疾病",
                "health_impact": "避免所有户外活动",
                "training": "❌ 避免所有户外训练，仅限室内",
                "sensitive": "❌ 所有人应停止户外活动",
                "protection": "必须外出时佩戴N95口罩",
                "indoor": "⚠️ 避免开窗通风，使用空气净化器"
            })

        # PM2.5特别建议
        if pm25 > 75:
            advice.append({
                "icon": "⚠️",
                "category": "PM2.5",
                "advice": f"PM2.5浓度较高({pm25} μg/m³)，对肺部有压力",
                "freediving": "⚠️ 自由潜水需特别注意，避免高强度闭气训练",
                "recommendation": "建议减少或暂停户外闭气训练，选择室内泳池或训练场馆"
            })

        return advice

    def get_training_recommendation(self):
        """生成综合训练建议"""
        recommendations = []

        # 基于准备度
        readiness_score = self.health_data.get("readiness", {}).get("score", 0)
        hrv_balance = self.health_data.get("readiness", {}).get("contributors", {}).get("hrv_balance", 0)
        recovery_index = self.health_data.get("readiness", {}).get("contributors", {}).get("recovery_index", 0)

        # 准备度评估
        if readiness_score >= 85:
            recommendations.append({
                "icon": "🔥",
                "level": "高强度",
                "priority": "primary",
                "title": "状态优秀",
                "readiness": f"准备度 {readiness_score}/100",
                "training": "✓ 可以进行高强度闭气训练",
                "details": [
                    "✓ 深度挑战",
                    "✓ 技术精练",
                    "✓ 极限闭气训练",
                    "✓ 爆发力训练"
                ]
            })
        elif readiness_score >= 70:
            recommendations.append({
                "icon": "💪",
                "level": "中等强度",
                "priority": "primary",
                "title": "状态良好",
                "readiness": f"准备度 {readiness_score}/100",
                "training": "✓ 适合中等强度训练",
                "details": [
                    "✓ 技术训练",
                    "✓ 中等深度潜水",
                    "✓ 有氧耐力训练",
                    "⚠️ 注意监测身体反应"
                ]
            })
        elif readiness_score >= 55:
            recommendations.append({
                "icon": "🚶",
                "level": "低强度",
                "priority": "warning",
                "title": "状态一般",
                "readiness": f"准备度 {readiness_score}/100",
                "training": "⚠️ 建议轻度训练或休息",
                "details": [
                    "⚠️ 恢复性训练",
                    "⚠️ 轻度技术练习",
                    "⚠️ 优先休息恢复",
                    "❌ 避免高强度训练"
                ]
            })
        else:
            recommendations.append({
                "icon": "🛌",
                "level": "休息",
                "priority": "alert",
                "title": "状态不佳",
                "readiness": f"准备度 {readiness_score}/100",
                "training": "❌ 建议完全休息",
                "details": [
                    "❌ 停止高强度训练",
                    "❌ 仅轻度活动",
                    "✓ 优先恢复睡眠",
                    "✓ 减轻训练负荷"
                ]
            })

        # HRV建议
        if hrv_balance < 60:
            recommendations.append({
                "icon": "😔",
                "level": "疲劳提醒",
                "priority": "warning",
                "title": f"HRV平衡偏低 ({hrv_balance}/100)",
                "meaning": "自主神经系统恢复不足",
                "recommendation": "可能存在疲劳累积",
                "action": [
                    "⚠️ 建议减少训练强度",
                    "⚠️ 增加休息时间",
                    "✓ 关注睡眠质量",
                    "✓ 可进行轻度活动促进恢复"
                ]
            })
        elif hrv_balance >= 85:
            recommendations.append({
                "icon": "😊",
                "level": "恢复优秀",
                "priority": "info",
                "title": f"HRV平衡优秀 ({hrv_balance}/100)",
                "meaning": "自主神经系统恢复良好",
                "recommendation": "神经系统状态佳，适合训练",
                "action": [
                    "✓ 可以进行正常训练计划",
                    "✓ 身体恢复能力良好",
                    "✓ 可以承受训练负荷"
                ]
            })

        # 恢复指数
        if recovery_index < 50:
            recommendations.append({
                "icon": "🔋",
                "level": "恢复不足",
                "priority": "warning",
                "title": f"恢复指数偏低 ({recovery_index}/100)",
                "meaning": "身体恢复不充分",
                "recommendation": "注意休息和睡眠质量",
                "action": [
                    "⚠️ 避免连续高强度训练",
                    "✓ 增加睡眠时间",
                    "✓ 可进行瑜伽、拉伸等恢复性活动",
                    "✓ 补充营养和水分"
                ]
            })

        # 结合天气
        if self.weather_data:
            temp = self.weather_data["current"]["temp_c"]
            precip_prob = self.weather_data["forecast"].get("precip_prob", 0)
            weather_desc = self.weather_data["current"]["weather_desc"]

            if temp < 10:
                recommendations.append({
                    "icon": "🥶",
                    "level": "天气限制",
                    "priority": "info",
                    "title": f"气温较低 ({temp}°C)",
                    "recommendation": "不适宜户外训练",
                    "action": [
                        "🏠 建议室内泳池训练",
                        "🏠 健身房力量训练",
                        "⚠️ 户外需充分热身",
                        "⚠️ 注意保暖"
                    ]
                })
            elif temp > 32:
                recommendations.append({
                    "icon": "🥵",
                    "level": "天气限制",
                    "priority": "info",
                    "title": f"气温较高 ({temp}°C)",
                    "recommendation": "注意防暑降温",
                    "action": [
                        "🏠 建议室内训练",
                        "⚠️ 避免正午户外训练",
                        "💧 充分补水",
                        "💧 注意电解质补充"
                    ]
                })

            if precip_prob > 70:
                recommendations.append({
                    "icon": "🌧️",
                    "level": "天气调整",
                    "priority": "info",
                    "title": f"降雨概率高 ({precip_prob:.0f}%)",
                    "recommendation": "建议调整训练计划",
                    "action": [
                        "🏠 建议室内训练",
                        "⏰ 等雨停后再训练",
                        "⚠️ 或选择室内泳池",
                        "☔ 携带雨具如必须户外"
                    ]
                })

        # 结合空气质量
        if self.aqi_data.get("aqi"):
            aqi = self.aqi_data["aqi"]

            if aqi > 100:
                recommendations.append({
                    "icon": "😷",
                    "level": "空气质量限制",
                    "priority": "warning",
                    "title": f"AQI {aqi} - 不适宜户外训练",
                    "recommendation": "建议室内训练",
                    "action": [
                        "🏠 室内泳池训练",
                        "❌ 避免户外有氧运动",
                        "😷 外出佩戴防护口罩",
                        "⚠️ 减少高强度呼吸训练"
                    ]
                })
            elif aqi > 150:
                recommendations.append({
                    "icon": "🚫",
                    "level": "空气质量警告",
                    "priority": "alert",
                    "title": f"AQI {aqi} - 避免户外活动",
                    "recommendation": "禁止户外训练",
                    "action": [
                        "🏠 仅限室内训练",
                        "❌ 禁止户外闭气训练",
                        "😷 必须外出时佩戴N95",
                        "🚪 关闭门窗，使用空气净化器"
                    ]
                })

        return recommendations

    def get_supplement_reminder(self):
        """生成补剂提醒"""
        day_of_month = self.today.day

        reminder = {
            "date": self.today_str,
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
        steps = self.health_data.get("activity", {}).get("steps", 0)

        if steps > 3000:
            reminder["conditional_supplements"].append({
                "name": "肌酸",
                "dose": "3g",
                "time": "训练前30分钟",
                "condition": "训练日"
            })

        return reminder

    def generate_markdown_dashboard(self):
        """生成Markdown格式的全面看板"""
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

            contributors = readiness.get("contributors", {})

            md += f"""
**分数：** {score}/100 {emoji} ({status})

| 指标 | 数值 | 状态 |
|------|------|------|
| HRV平衡 | {contributors.get('hrv_balance', 0)}/100 | {'✓ 优秀' if contributors.get('hrv_balance', 0) >= 80 else '⚠️ 需关注' if contributors.get('hrv_balance', 0) >= 60 else '❌ 偏低'} |
| 恢复指数 | {contributors.get('recovery_index', 0)}/100 | {'✓ 优秀' if contributors.get('recovery_index', 0) >= 80 else '⚠️ 需关注' if contributors.get('recovery_index', 0) >= 50 else '❌ 偏低'} |
| 静息心率 | {contributors.get('resting_heart_rate', 0)}/100 | - |
| 睡眠平衡 | {contributors.get('sleep_balance', 0)}/100 | {'✓ 优秀' if contributors.get('sleep_balance', 0) >= 80 else '⚠️ 需关注'} |
| 活动平衡 | {contributors.get('activity_balance', 0)}/100 | {'✓ 优秀' if contributors.get('activity_balance', 0) >= 80 else '⚠️ 需关注'} |

"""
        else:
            md += "\n⚠️ 今日暂无准备度数据\n\n"

        # 睡眠
        md += "### 😴 睡眠质量\n\n"

        if self.health_data.get("sleep"):
            sleep = self.health_data["sleep"]
            score = sleep.get("score", 0)
            total_hours = sleep.get("total_sleep_duration", 0) / 3600
            deep_hours = sleep.get("total_deep", 0) / 3600
            rem_hours = sleep.get("total_rem", 0) / 3600
            efficiency = sleep.get("sleep_efficiency", 0)

            md += f"""**分数：** {score}/100

| 指标 | 数值 | 评价 |
|------|------|------|
| 总睡眠时长 | {total_hours:.1f} 小时 | {'✓' if 7 <= total_hours <= 9 else '⚠️'} |
| 深度睡眠 | {deep_hours:.1f} 小时 ({deep_hours/total_hours*100 if total_hours > 0 else 0:.1f}%) | {'✓ 正常' if total_hours > 0 and 15 <= deep_hours/total_hours*100 <= 25 else '⚠️'} |
| 快速眼动睡眠 | {rem_hours:.1f} 小时 ({rem_hours/total_hours*100 if total_hours > 0 else 0:.1f}%) | {'✓ 正常' if total_hours > 0 and 20 <= rem_hours/total_hours*100 <= 25 else '⚠️'} |
| 睡眠效率 | {efficiency:.1f}% | {'✓ 优秀' if efficiency >= 85 else '⚠️ 需改善'} |
| 入睡时间 | {sleep.get('onset_latency', 0)/60:.1f} 分钟 | {'✓ 正常' if sleep.get('onset_latency', 0) < 1800 else '⚠️ 较长'} |
| 平均心率 | {sleep.get('average_hr', 0):.0f} bpm | - |
| 最低心率 | {sleep.get('lowest_hr', 0):.0f} bpm | - |
| 平均HRV | {sleep.get('average_hrv', 0):.0f} ms | {'✓ 优秀' if sleep.get('average_hrv', 0) >= 50 else '⚠️ 需关注'} |

"""
        else:
            md += "⚠️ 昨晚暂无睡眠数据\n\n"

        # 活动
        md += "### 🏃 活动数据\n\n"

        if self.health_data.get("activity"):
            activity = self.health_data["activity"]
            score = activity.get("score", 0)

            md += f"""**分数：** {score}/100

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

            md += f"""### 当前天气 - {CITY_NAME}

**{current.get('weather_desc', '')}** | 温度 {current.get('temp_c', 0)}°C | 体感 {current.get('feels_like_c', 0)}°C

| 指标 | 数值 |
|------|------|
| 温度 | {current.get('temp_c', 0)}°C |
| 体感温度 | {current.get('feels_like_c', 0)}°C |
| 湿度 | {current.get('humidity', 0)}% |
| 风速 | {current.get('wind_speed_kmh', 0):.1f} km/h |
| 气压 | {current.get('pressure', 0):.0f} hPa |
| 紫外线指数 | UV {forecast.get('uv_index', 0)} |

### 今日预报

| 指标 | 数值 |
|------|------|
| 最高温度 | {forecast.get('max_temp_c', 0)}°C |
| 最低温度 | {forecast.get('min_temp_c', 0)}°C |
| 最高体感 | {forecast.get('max_feels_like_c', 0)}°C |
| 最低体感 | {forecast.get('min_feels_like_c', 0)}°C |
| 降水量 | {forecast.get('precipitation_mm', 0)} mm |
| 降雨量 | {forecast.get('rain_mm', 0)} mm |
| 降水概率 | {forecast.get('precip_prob', 0):.0f}% |
| 日出 | {forecast.get('sunrise', '')} |
| 日落 | {forecast.get('sunset', '')} |

"""
        else:
            md += "⚠️ 天气数据暂无\n\n"

        # 穿着建议
        md += "### 👔 穿着建议\n\n"

        clothing_advice = self.get_clothing_advice()
        for item in clothing_advice:
            md += f"**{item['icon']} {item['category']}：** {item['advice']}\n\n"

        # 空气质量
        md += "\n---\n\n## 🌬️ 空气质量\n\n"

        if self.aqi_data.get("aqi"):
            aqi = self.aqi_data["aqi"]
            pm25 = self.aqi_data.get("pm25", 0)

            aqi_status = "🟢 优" if aqi <= 50 else "🟡 良" if aqi <= 100 else "🟠 轻度污染" if aqi <= 150 else "🔴 中度污染" if aqi <= 200 else "🟣 重度污染"

            md += f"""### AQI 指数：**{aqi}** {aqi_status}

| 指标 | 数值 | 标准 |
|------|------|------|
| PM2.5 | {pm25} μg/m³ | {'✓ 优' if pm25 <= 35 else '⚠️ 超标' if pm25 <= 75 else '❌ 污染'} |
| PM10 | {self.aqi_data.get('pm10', 0)} μg/m³ | {'✓ 优' if self.aqi_data.get('pm10', 0) <= 50 else '⚠️ 超标'} |
| 臭氧 (O₃) | {self.aqi_data.get('o3', 0)} μg/m³ | - |
| 二氧化氮 (NO₂) | {self.aqi_data.get('no2', 0)} μg/m³ | - |
| 二氧化硫 (SO₂) | {self.aqi_data.get('so2', 0)} μg/m³ | - |

### 空气质量建议

"""

            aqi_advice = self.get_aqi_advice()
            for item in aqi_advice:
                md += f"**{item['icon']} {item['category']}：** {item.get('advice', '')}\n\n"
                for key in ["health_impact", "training", "sensitive", "protection", "freediving", "indoor"]:
                    if key in item:
                        md += f"- **{key}：** {item[key]}\n"
                md += "\n"

        else:
            md += "⚠️ 空气质量数据暂无\n\n"

        # 训练建议
        md += "\n---\n\n## 🎯 训练建议\n\n"

        recommendations = self.get_training_recommendation()

        for i, rec in enumerate(recommendations, 1):
            md += f"### {rec.get('icon', '')} {rec.get('level', '')}\n\n"
            md += f"**{rec.get('title', '')}**\n\n"
            if rec.get('readiness'):
                md += f"{rec.get('readiness', '')}\n\n"
            if rec.get('training'):
                md += f"**训练建议：** {rec.get('training', '')}\n\n"
            if rec.get('details'):
                md += "**详细建议：**\n\n"
                for detail in rec['details']:
                    md += f"{detail}\n"
                md += "\n"
            if rec.get('action'):
                md += "**行动建议：**\n\n"
                for action in rec['action']:
                    md += f"{action}\n"
                md += "\n"

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
                md += f"- ☑ **{supp['name']}** - {supp['dose']} ({supp.get('condition', '')})\n"

        # 数据文件位置
        md += f"""

---

## 📋 数据文件位置

- **Markdown报告：** `DailyReports/dashboard_{self.today_str}.md`
- **JSON数据：** `DailyReports/dashboard_{self.today_str}.json`

---

*报告生成时间：{self.today.strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源：Oura Ring Gen 3 + Open-Meteo天气API + WAQI空气质量API*
*天气数据来源：Open-Meteo（基于ECMWF和GFS数据）*
*空气质量来源：WAQI.info（全球空气质量监测网络）*
"""

        return md

    def generate(self):
        """生成所有格式的报告"""
        print("=" * 60)
        print("金明 - 全面健康看板（V2 - 高质量API）")
        print("=" * 60)

        # 获取所有数据
        self.get_oura_data()
        self.get_qweather_data()
        self.get_waqi_aqi_data()

        # 生成Markdown报告
        md_content = self.generate_markdown_dashboard()
        md_file = self.dashboard_dir / f"dashboard_{self.today_str}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"\n✓ Markdown报告已保存: {md_file}")

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
        print(f"\n📍 报告位置: {md_file}")

        return md_content

def main():
    """主函数"""
    dashboard = ComprehensiveHealthDashboardV2()
    dashboard.generate()

if __name__ == "__main__":
    main()
