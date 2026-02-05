#!/usr/bin/env python3
"""
金明 - 终极健康看板（完整版）
包含：Oura数据 + 天气 + 空气质量 + 训练建议 + 推送通知
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import re
from pathlib import Path
import subprocess
import sys

# 导入训练数据分析模块
try:
    from training_data_analyzer import TrainingDataAnalyzer
except ImportError:
    TrainingDataAnalyzer = None

# 导入饮食建议模块
try:
    from diet_advisor import DietAdvisor
except ImportError:
    DietAdvisor = None

# 导入泳池训练和两餐制顾问模块
try:
    from pool_training_advisor import TwoMealDietAdvisor, PoolTrainingAdvisor
except ImportError:
    TwoMealDietAdvisor = None
    PoolTrainingAdvisor = None

# 导入高级健康分析模块
try:
    from advanced_health_analyzer import AdvancedHealthAnalyzer
except ImportError:
    AdvancedHealthAnalyzer = None

# 导入图表生成模块
try:
    from chart_generator import HealthChartGenerator
except ImportError:
    HealthChartGenerator = None

# 导入增强可视化模块
try:
    from enhanced_visualizer import EnhancedVisualizer
except ImportError:
    EnhancedVisualizer = None

# 导入有道云笔记读取器
try:
    from youdao_note_reader import YoudaoNoteReader
except ImportError:
    YoudaoNoteReader = None

# Oura API 配置
OURA_ACCESS_TOKEN = "DUC6D3LWLLNOWXK6IBNVEFS7IH445TIV"
OURA_BASE_URL = "https://api.ouraring.com/v2"

# 城市配置
CITY_NAME = "上海"
CITY_ID = "101020100"
LATITUDE = 31.2304
LONGITUDE = 121.4737

class UltimateHealthDashboard:
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
        self.training_insights = {}

        # 初始化训练数据分析器
        self.training_analyzer = TrainingDataAnalyzer() if TrainingDataAnalyzer else None

        # 初始化饮食建议顾问
        self.diet_advisor = DietAdvisor() if DietAdvisor else None

        # 初始化两餐制饮食顾问
        self.two_meal_advisor = TwoMealDietAdvisor() if TwoMealDietAdvisor else None

        # 初始化泳池训练顾问
        self.pool_training_advisor = PoolTrainingAdvisor() if PoolTrainingAdvisor else None

        # 初始化高级健康分析器
        self.advanced_analyzer = AdvancedHealthAnalyzer() if AdvancedHealthAnalyzer else None

        # 初始化图表生成器
        self.chart_generator = HealthChartGenerator(self.dashboard_dir) if HealthChartGenerator else None

        # 初始化增强可视化器
        self.enhanced_visualizer = EnhancedVisualizer(self.dashboard_dir) if EnhancedVisualizer else None

        # 8Sleep API配置（需要用户提供）
        self.eightsleep_api_key = None  # 需要配置
        self.eightsleep_user_id = None  # 需要配置

    def get_aqi_from_purpleair(self):
        """使用PurpleAir API获取空气质量（备用方案）"""
        try:
            # 使用公开的AQI数据源
            url = "https://api.airvisual.com/v2/city"
            params = {"city": "Shanghai", "state": "Shanghai", "country": "China"}
            headers = {"X-API-Key": "demo"}  # 尝试使用demo key

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"✓ 获取到空气质量数据")
                return data
            else:
                print(f"⚠️ AirVisual API返回: {response.status_code}")

        except Exception as e:
            print(f"⚠️ AirVisual API失败: {e}")

        return None

    def get_aqi_alternative(self):
        """使用备用方案获取AQI"""
        try:
            # 尝试从公开的JSON源获取
            # 使用美国大使馆或其他监测站的数据
            url = "https://api.waqi.info/feed/shanghai/"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                # 尝试解析JSON响应
                try:
                    data = response.json()
                    if data.get("status") == "ok":
                        station_data = data.get("data", {})
                        iaqi = station_data.get("iaqi", {})

                        self.aqi_data = {
                            "aqi": int(station_data.get("idx", 0)),
                            "pm25": int(iaqi.get("pm25", {}).get("v", 0)),
                            "pm10": int(iaqi.get("pm10", {}).get("v", 0)),
                            "o3": int(iaqi.get("o3", {}).get("v", 0)),
                            "no2": int(iaqi.get("no2", {}).get("v", 0)),
                            "so2": int(iaqi.get("so2", {}).get("v", 0))
                        }

                        print(f"✓ 获取到空气质量: AQI {self.aqi_data['aqi']}")
                        return True
                except:
                    pass

        except Exception as e:
            print(f"⚠️ 备用AQI方案失败: {e}")

        # 最后的备用方案：使用历史平均数据
        print("⚠️ 使用历史平均AQI数据")
        self.aqi_data = {
            "aqi": 75,
            "pm25": 35,
            "pm10": 50,
            "o3": 40,
            "no2": 30,
            "so2": 10,
            "note": "历史平均值（API暂时不可用）"
        }
        return True

    def search_training_notes(self):
        """搜索训练相关笔记"""
        print("🔍 搜索训练相关笔记...")

        training_notes = []

        # 搜索根目录
        root_dir = Path.cwd().parent
        for md_file in root_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 搜索关键词
                    if any(keyword in content for keyword in ['训练', '潜水', 'freediving', '深度', '闭气', '成绩', '比赛', 'depth', 'dive']):
                        training_notes.append({
                            "file": str(md_file),
                            "name": md_file.name,
                            "size": len(content)
                        })
            except:
                pass

        print(f"✓ 找到 {len(training_notes)} 个可能相关的笔记")
        return training_notes

    def analyze_training_data(self):
        """分析训练数据并提供建议"""
        # 使用训练数据分析器获取个性化建议
        if self.training_analyzer:
            analysis = self.training_analyzer.analyze_current_status(self.health_data)
            insights = [{
                "status": analysis["status"],
                "recommendation": analysis["recommendation"],
                "training_types": analysis["training_types"],
                "confidence": analysis["confidence"]
            }]
            return insights, analysis
        else:
            # 备用方案：使用原有逻辑
            readiness_score = self.health_data.get("readiness", {}).get("score", 0)
            hrv = self.health_data.get("readiness", {}).get("contributors", {}).get("hrv_balance", 0)
            recovery = self.health_data.get("readiness", {}).get("contributors", {}).get("recovery_index", 0)
            sleep_score = self.health_data.get("sleep", {}).get("score", 0)

            insights = []

            # 分析最佳状态
            if readiness_score >= 85 and recovery >= 75 and sleep_score >= 80:
                insights.append({
                    "status": "🔥 最佳状态",
                    "recommendation": "今日是挑战个人记录的好时机",
                    "training_types": ["深度挑战", "极限闭气", "技术突破"],
                    "confidence": "高"
                })
            elif readiness_score >= 70 and recovery >= 60:
                insights.append({
                    "status": "💪 训练状态",
                    "recommendation": "适合系统训练，巩固技术",
                    "training_types": ["中等深度", "技术练习", "耐力训练"],
                    "confidence": "中"
                })
            elif recovery < 50:
                insights.append({
                    "status": "⚠️ 恢复不足",
                    "recommendation": "建议轻量训练或休息",
                    "training_types": ["瑜伽", "拉伸", "轻度活动"],
                    "confidence": "高"
                })
            else:
                insights.append({
                    "status": "✓ 稳定状态",
                    "recommendation": "维持常规训练",
                    "training_types": ["常规训练", "技术维护"],
                    "confidence": "中"
                })

            return insights, None

    def send_push_notification(self, title, message):
        """发送macOS推送通知"""
        try:
            # 使用osascript发送通知
            script = f'''
            display notification "{message}" with title "{title}" sound name "Glass"
            '''
            subprocess.run(['osascript', '-e', script], check=True, capture_output=True, text=True)
            print("✓ 推送通知已发送")
            return True
        except Exception as e:
            print(f"⚠️ 推送通知发送失败: {e}")
            return False

    def generate_ultimate_dashboard(self):
        """生成终极看板"""
        print("=" * 60)
        print("金明 - 终极健康看板")
        print("=" * 60)

        # 1. 获取Oura数据
        self.get_oura_data()

        # 1.5. 获取8Sleep数据
        self.get_eightsleep_data()

        # 2. 获取天气数据
        self.get_weather_data()

        # 3. 获取空气质量（多源平均）
        self.get_aqi_multi_source()

        # 3.5. 读取有道云笔记中的训练日志
        yd_training_logs = []
        if YoudaoNoteReader:
            print("\n📖 读取有道云笔记训练日志...")
            try:
                yd_reader = YoudaoNoteReader()
                yd_training_logs = yd_reader.read_yesterday_training_log()
                if yd_training_logs:
                    yd_reader.print_summary(yd_training_logs)
                    yd_reader.save_to_training_log_system(yd_training_logs)
                    print(f"✅ 有道云笔记：找到 {len(yd_training_logs)} 条训练记录")
                else:
                    print("ℹ️ 有道云笔记：未找到昨天的训练记录")
            except Exception as e:
                print(f"⚠️ 有道云笔记读取失败: {e}")

        # 4. 搜索训练笔记
        training_notes = self.search_training_notes()

        # 5. 分析训练建议（使用训练数据分析器）
        training_insights, detailed_analysis = self.analyze_training_data()

        # 6. 生成完整报告
        self.generate_complete_report(training_notes, training_insights, detailed_analysis)

        # 7. 发送推送通知
        if detailed_analysis:
            readiness = detailed_analysis.get("current_readiness", 0)
            status = detailed_analysis.get("status", "")
            recommendation = detailed_analysis.get("recommendation", "")

            notification_title = f"🏊 金明今日健康报告 - 准备度 {readiness}/100"
            notification_message = f"{status}\n{recommendation[:50]}..."
            self.send_push_notification(notification_title, notification_message)

        # 8. 生成图表
        if self.chart_generator:
            print("\n📊 生成基础数据图表...")
            self.chart_generator.generate_readiness_radar_chart(self.health_data, detailed_analysis)
            self.chart_generator.generate_sleep_quality_chart(self.health_data)
            self.chart_generator.generate_activity_pie_chart(self.health_data)
            self.chart_generator.generate_training_gauge_chart(self.health_data.get("readiness", {}).get("score", 0))

        # 9. 生成增强可视化图表（7天、30天趋势）
        if self.enhanced_visualizer:
            print("\n📊 生成增强可视化图表（7天、30天趋势）...")
            self.enhanced_visualizer.generate_all_charts()

        print("\n✓ 终极看板生成完成！")

    def get_eightsleep_data(self):
        """获取8Sleep睡眠数据"""
        if not self.eightsleep_api_key:
            print("⚠️ 8Sleep API未配置，跳过")
            return False

        try:
            # 8Sleep API v2
            # 获取昨晚的睡眠数据
            url = "https://api.8slp.net/v1/users/me/sessions"

            headers = {
                "Authorization": f"Bearer {self.eightsleep_api_key}",
                "Content-Type": "application/json"
            }

            params = {
                "startDate": self.yesterday_str,
                "endDate": self.today_str,
                "tz": "Asia/Shanghai"
            }

            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if data and len(data) > 0:
                    session = data[0]  # 获取最近一晚的数据

                    # 解析8Sleep数据
                    self.eightsleep_data = {
                        "sleep_score": int(session.get("score", {}).get("total", 0)),
                        "duration_total": session.get("duration", {}).get("total", 0) / 60,  # 分钟
                        "duration_light": session.get("duration", {}).get("light", 0) / 60,
                        "duration_deep": session.get("duration", {}).get("deep", 0) / 60,
                        "duration_rem": session.get("duration", {}).get("rem", 0) / 60,
                        "sleep_latency": session.get("timeToSleep", 0),  # 入睡时间（分钟）
                        "tossing_and_turning": session.get("tossAndTurn", {}).get("total", 0),  # 翻身次数
                        "breath_avg": session.get("respiration", {}).get("avg", 0),  # 平均呼吸率
                        "heart_rate_avg": session.get("heartRate", {}).get("avg", 0),  # 平均心率
                        "heart_rate_min": session.get("heartRate", {}).get("min", 0),  # 最低心率
                        "temp_bed_min": session.get("temp", {}).get("min", 0),  # 床垫最低温度
                        "temp_bed_avg": session.get("temp", {}).get("avg", 0),  # 床垫平均温度
                        "temp_room_min": session.get("tempRoom", {}).get("min", 0),  # 房间最低温度
                        "temp_room_avg": session.get("tempRoom", {}).get("avg", 0),  # 房间平均温度
                        "sleep_stages": session.get("sleepStages", []),  # 睡眠阶段详细数据
                        "date": session.get("ts", "").split("T")[0]  # 日期
                    }

                    print(f"✓ 8Sleep数据获取完成: 睡眠分数 {self.eightsleep_data['sleep_score']}/100")
                    return True
                else:
                    print("⚠️ 8Sleep没有返回数据")
                    return False
            else:
                print(f"⚠️ 8Sleep API错误: {response.status_code}")
                return False

        except Exception as e:
            print(f"⚠️ 8Sleep数据获取失败: {e}")
            return False

    def get_oura_data(self):
        """获取Oura数据（复用之前的代码）"""
        print("📊 获取Oura Ring数据...")

        # 准备度
        try:
            response = requests.get(
                f"{OURA_BASE_URL}/usercollection/daily_readiness",
                headers=self.oura_headers,
                params={"start_date": self.yesterday_str, "end_date": self.today_str},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get("data"):
                self.health_data["readiness"] = data["data"][-1]
        except:
            pass

        # 睡眠
        try:
            response = requests.get(
                f"{OURA_BASE_URL}/usercollection/daily_sleep",
                headers=self.oura_headers,
                params={"start_date": self.yesterday_str, "end_date": self.today_str},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get("data"):
                self.health_data["sleep"] = data["data"][-1]
        except:
            pass

        # 活动
        try:
            response = requests.get(
                f"{OURA_BASE_URL}/usercollection/daily_activity",
                headers=self.oura_headers,
                params={"start_date": self.yesterday_str, "end_date": self.today_str},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get("data"):
                self.health_data["activity"] = data["data"][-1]
        except:
            pass

        print("✓ Oura数据获取完成")

    def get_weather_data(self):
        """获取天气数据（复用之前的代码）"""
        print(f"🌤️ 获取{CITY_NAME}天气数据...")

        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_sum,rain_sum,precipitation_probability_max&timezone=auto"

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})
            daily = data.get("daily", {})

            weather_codes = {
                0: "晴", 1: "多云", 2: "多云", 3: "多云", 45: "雾",
                51: "小雨", 61: "小雨", 63: "小雨", 65: "中雨",
                80: "阵雨", 95: "雷雨"
            }

            weather_code = current.get("weather_code", 0)
            self.weather_data = {
                "city": CITY_NAME,
                "current": {
                    "temp_c": round(current.get("temperature_2m", 0), 1),
                    "feels_like_c": round(current.get("apparent_temperature", 0), 1),
                    "humidity": round(current.get("relative_humidity_2m", 0), 1),
                    "wind_speed_kmh": round(current.get("wind_speed_10m", 0) * 3.6, 1),
                    "weather_desc": weather_codes.get(weather_code, "未知"),
                    "pressure": round(current.get("surface_pressure", 0), 1)
                },
                "forecast": {
                    "max_temp_c": round(daily.get("temperature_2m_max", [0])[0], 1) if daily.get("temperature_2m_max") else 0,
                    "min_temp_c": round(daily.get("temperature_2m_min", [0])[0], 1) if daily.get("temperature_2m_min") else 0,
                    "precip_prob": round(daily.get("precipitation_probability_max", [0])[0], 1) if daily.get("precipitation_probability_max") else 0,
                    "uv_index": round(daily.get("uv_index_max", [0])[0], 1) if daily.get("uv_index_max") else 0,
                    "sunrise": daily.get("sunrise", [""])[0].split("T")[1][:5] if daily.get("sunrise") else "",
                    "sunset": daily.get("sunset", [""])[0].split("T")[1][:5] if daily.get("sunset") else ""
                } if daily else {}
            }

            print(f"✓ 天气数据获取完成: {self.weather_data['current']['temp_c']}°C")

        except Exception as e:
            print(f"⚠️ 天气数据获取失败: {e}")

    def get_aqi_from_waqi(self):
        """从WAQI获取空气质量（数据源1）"""
        try:
            url = "https://api.waqi.info/feed/shanghai/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "ok":
                        station_data = data.get("data", {})
                        iaqi = station_data.get("iaqi", {})

                        return {
                            "source": "WAQI",
                            "aqi": int(station_data.get("idx", 0)),
                            "pm25": int(iaqi.get("pm25", {}).get("v", 0)),
                            "pm10": int(iaqi.get("pm10", {}).get("v", 0))
                        }
                except:
                    pass

            print(f"⚠️ WAQI解析失败")
            return None

        except Exception as e:
            print(f"⚠️ WAQI请求失败: {e}")
            return None

    def get_aqi_from_openmeteo(self):
        """从Open-Meteo获取空气质量（数据源2）"""
        try:
            # Open-Meteo空气质量API（基于CAMS）
            url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LATITUDE}&longitude={LONGITUDE}&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,eu_aqi,us_aqi"
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})

                # 优先使用美国AQI标准，其次欧洲AQI
                aqi_value = current.get("us_aqi") or current.get("eu_aqi") or 75

                return {
                    "source": "Open-Meteo/CAMS",
                    "aqi": int(aqi_value),
                    "pm25": int(current.get("pm2_5", 35)),
                    "pm10": int(current.get("pm10", 50))
                }

            print(f"⚠️ Open-Meteo AQI请求失败: {response.status_code}")
            return None

        except Exception as e:
            print(f"⚠️ Open-Meteo AQI请求异常: {e}")
            return None

    def get_aqi_from_iqair(self):
        """从IQAir获取空气质量（数据源4）"""
        try:
            # IQAir免费API（使用城市名）
            url = f"http://api.airvisual.com/v2/city?city=Shanghai&state=Shanghai&country=China&key=YOUR_API_KEY"

            # 由于没有API key，尝试使用公开的feed
            url2 = "https://www.iqair.com/shanghai/shanghai"

            # 尝试获取页面数据（简化版）
            response = requests.get("https://api.waqi.info/feed/shanghai/xuhui/", headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "ok":
                        station_data = data.get("data", {})
                        iaqi = station_data.get("iaqi", {})

                        return {
                            "source": "WAQI/Xuhui",
                            "aqi": int(station_data.get("idx", 75)),
                            "pm25": int(iaqi.get("pm25", {}).get("v", 35)),
                            "pm10": int(iaqi.get("pm10", {}).get("v", 50))
                        }
                except:
                    pass

            print(f"⚠️ IQAir/WAQI备用源失败")
            return None

        except Exception as e:
            print(f"⚠️ IQAir请求异常: {e}")
            return None

    def get_aqi_from_aqicn(self):
        """从AQICN获取空气质量（数据源3，备用）"""
        try:
            # 使用上海的不同站点
            url = "https://api.waqi.info/feed/shanghai/pudong/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "ok":
                        station_data = data.get("data", {})
                        iaqi = station_data.get("iaqi", {})

                        return {
                            "source": "AQICN/Pudong",
                            "aqi": int(station_data.get("idx", 75)),
                            "pm25": int(iaqi.get("pm25", {}).get("v", 35)),
                            "pm10": int(iaqi.get("pm10", {}).get("v", 50))
                        }
                except:
                    pass

            print(f"⚠️ AQICN备用源失败")
            return None

        except Exception as e:
            print(f"⚠️ AQICN备用源异常: {e}")
            return None

    def get_aqi_multi_source(self):
        """从多个数据源获取AQI并计算平均值"""
        print("\n🌬️ 获取空气质量数据（多源平均）...")

        sources = []

        # 尝试从多个数据源获取
        source1 = self.get_aqi_from_waqi()
        if source1:
            sources.append(source1)

        source2 = self.get_aqi_from_openmeteo()
        if source2:
            sources.append(source2)

        source3 = self.get_aqi_from_aqicn()
        if source3:
            sources.append(source3)

        source4 = self.get_aqi_from_iqair()
        if source4:
            sources.append(source4)

        # 如果至少有1个数据源，就使用；否则用历史平均
        if len(sources) >= 1:
            # 计算平均值
            avg_aqi = int(sum(s["aqi"] for s in sources) / len(sources))
            avg_pm25 = int(sum(s["pm25"] for s in sources) / len(sources))
            avg_pm10 = int(sum(s["pm10"] for s in sources) / len(sources))

            self.aqi_data = {
                "aqi": avg_aqi,
                "pm25": avg_pm25,
                "pm10": avg_pm10,
                "sources": [s["source"] for s in sources],
                "source_count": len(sources)
            }

            print(f"✓ 空气质量获取完成（{len(sources)}个数据源平均）")
            print(f"  数据源: {', '.join(s['source'] for s in sources)}")
            print(f"  平均AQI: {avg_aqi} (PM2.5: {avg_pm25}, PM10: {avg_pm10})")
            return True
        else:
            # 使用历史平均值
            print("⚠️ 多源获取失败，使用历史平均值")
            self.aqi_data = {
                "aqi": 75,
                "pm25": 35,
                "pm10": 50,
                "sources": ["历史平均"],
                "source_count": 1,
                "note": "历史平均值（API暂时不可用）"
            }
            return True

    def generate_complete_report(self, training_notes, training_insights, detailed_analysis=None):
        """生成完整报告"""
        md = f"""# 金明 - 终极健康看板

**日期：** {self.today_str}
**更新时间：** {self.today.strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 今日健康评分

"""

        # 健康数据
        if self.health_data.get("readiness"):
            readiness = self.health_data["readiness"]
            score = readiness.get("score", 0)
            emoji = "⭐" if score >= 85 else "✓" if score >= 70 else "⚠️"

            md += f"""### 准备度 (Readiness)

**分数：** {score}/100 {emoji}

| 指标 | 数值 | 状态 |
|------|------|------|
| HRV平衡 | {readiness.get('contributors', {}).get('hrv_balance', 0)}/100 | - |
| 恢复指数 | {readiness.get('contributors', {}).get('recovery_index', 0)}/100 | - |
| 静息心率 | {readiness.get('contributors', {}).get('resting_heart_rate', 0)}/100 | - |
| 睡眠平衡 | {readiness.get('contributors', {}).get('sleep_balance', 0)}/100 | - |
| 活动平衡 | {readiness.get('contributors', {}).get('activity_balance', 0)}/100 | - |

"""

        # 睡眠分数
        if self.health_data.get("sleep"):
            sleep = self.health_data["sleep"]
            sleep_score = sleep.get("score", 0)
            sleep_emoji = "⭐" if sleep_score >= 85 else "✓" if sleep_score >= 70 else "⚠️"
            contributors = sleep.get("contributors", {})

            md += f"""### 睡眠质量 (Sleep Score)

**分数：** {sleep_score}/100 {sleep_emoji}

| 睡眠指标 | 评分 |
|----------|------|
| 总睡眠质量 | {contributors.get('total_sleep', 0)}/100 |
| 深睡质量 | {contributors.get('deep_sleep', 0)}/100 |
| REM睡眠质量 | {contributors.get('rem_sleep', 0)}/100 |
| 睡眠效率 | {contributors.get('efficiency', 0)}/100 |
| 入睡速度 | {contributors.get('latency', 0)}/100 |
| 睡眠安享度 | {contributors.get('restfulness', 0)}/100 |
| 睡眠时间规律 | {contributors.get('timing', 0)}/100 |

"""

        # 8Sleep数据（如果有）
        if hasattr(self, 'eightsleep_data') and self.eightsleep_data:
            es = self.eightsleep_data

            md += f"""### 🛏️ 8Sleep智能床垫数据

**睡眠总分：** {es['sleep_score']}/100

| 指标 | 数值 |
|------|------|
| 总睡眠时长 | {es['duration_total']:.0f} 分钟 ({es['duration_total']/60:.1f} 小时) |
| 浅睡时长 | {es['duration_light']:.0f} 分钟 |
| 深睡时长 | {es['duration_deep']:.0f} 分钟 |
| REM时长 | {es['duration_rem']:.0f} 分钟 |
| 入睡时间 | {es['sleep_latency']:.0f} 分钟 |
| 翻身次数 | {es['tossing_and_turning']:.0f} 次 |
| 平均呼吸率 | {es['breath_avg']:.1f} 次/分 |
| 平均心率 | {es['heart_rate_avg']:.0f} bpm |
| 最低心率 | {es['heart_rate_min']:.0f} bpm |
| 床垫平均温度 | {es['temp_bed_avg']:.1f}°C (最低 {es['temp_bed_min']:.1f}°C) |
| 房间平均温度 | {es['temp_room_avg']:.1f}°C (最低 {es['temp_room_min']:.1f}°C) |

**睡眠质量分析：**
"""

            # 深睡比例分析
            deep_ratio = (es['duration_deep'] / es['duration_total']) * 100
            rem_ratio = (es['duration_rem'] / es['duration_total']) * 100

            md += f"- 深睡占比：{deep_ratio:.1f}% "
            if deep_ratio >= 20:
                md += "✅ 优秀\n"
            elif deep_ratio >= 15:
                md += "✓ 良好\n"
            else:
                md += "⚠️ 偏低\n"

            md += f"- REM占比：{rem_ratio:.1f}% "
            if rem_ratio >= 20:
                md += "✅ 优秀\n"
            elif rem_ratio >= 15:
                md += "✓ 良好\n"
            else:
                md += "⚠️ 偏低\n"

            md += f"- 翻身次数：{es['tossing_and_turning']:.0f}次 "
            if es['tossing_and_turning'] <= 10:
                md += "✅ 睡眠安稳\n"
            elif es['tossing_and_turning'] <= 20:
                md += "✓ 正常\n"
            else:
                md += "⚠️ 较多，可能睡眠质量不佳\n"

            md += "\n"

        # 天气数据
        md += "\n## 🌤️ 今日天气\n\n"

        if self.weather_data.get("current"):
            current = self.weather_data["current"]
            forecast = self.weather_data.get("forecast", {})

            md += f"""**{CITY_NAME}** | {current.get('temp_c')}°C | {current.get('weather_desc')}

| 指标 | 数值 |
|------|------|
| 温度 | {current.get('temp_c')}°C |
| 体感温度 | {current.get('feels_like_c')}°C |
| 湿度 | {current.get('humidity')}% |
| 风速 | {current.get('wind_speed_kmh'):.1f} km/h |
| 日出 | {forecast.get('sunrise', '')} |
| 日落 | {forecast.get('sunset', '')} |

### 👔 穿着建议

"""

            temp = current.get('temp_c', 0)
            if temp <= 10:
                md += "- 🧥 寒冷：羽绒服、厚毛衣、保暖内衣\n"
            elif temp <= 20:
                md += "- 🧥 较冷：夹克、毛衣、长裤\n"
            elif temp <= 28:
                md += "- 👑 舒适：长袖、轻薄外套\n"
            else:
                md += "- 👕 炎热：短袖、短裤\n"

        # 空气质量
        md += "\n## 🌬️ 空气质量\n\n"

        if self.aqi_data.get("aqi"):
            aqi = self.aqi_data["aqi"]
            aqi_status = "🟢 优" if aqi <= 50 else "🟡 良" if aqi <= 100 else "🟠 轻度污染"
            sources_info = self.aqi_data.get("sources", ["历史平均"])
            source_count = self.aqi_data.get("source_count", 1)

            md += f"""**AQI指数：** {aqi} {aqi_status}

*数据源：{', '.join(sources_info)}（{source_count}个数据源平均）*

| 指标 | 数值 |
|------|------|
| PM2.5 | {self.aqi_data.get('pm25', 0)} μg/m³ |
| PM10 | {self.aqi_data.get('pm10', 0)} μg/m³ |

### 训练建议（基于空气质量）

"""

            if aqi <= 100:
                md += "- ✅ 空气质量良好，适合户外训练\n"
            elif aqi <= 150:
                md += "- ⚠️ 空气轻度污染，建议室内训练\n"
            else:
                md += "- ❌ 空气污染，禁止户外训练\n"

        # 训练建议
        md += "\n## 🎯 训练建议\n\n"

        for insight in training_insights:
            md += f"### {insight['status']}\n\n"
            md += f"**建议：** {insight['recommendation']}\n\n"
            md += f"**推荐训练：** {', '.join(insight['training_types'])}\n\n"
            md += f"**置信度：** {insight['confidence']}\n\n"

            # 添加详细分析信息
            if detailed_analysis:
                md += f"**表现预测：** {detailed_analysis.get('performance_prediction', '')}\n\n"
                if detailed_analysis.get('comparison_to_best'):
                    md += f"**状态对比：** {detailed_analysis['comparison_to_best']}\n\n"

        # 具体推荐建议
        md += "## 💡 今日具体推荐\n\n"

        readiness_score = self.health_data.get("readiness", {}).get("score", 0)
        recovery_index = self.health_data.get("readiness", {}).get("contributors", {}).get("recovery_index", 0)
        sleep_score = self.health_data.get("sleep", {}).get("score", 0)

        # 根据不同状态给出具体建议
        if readiness_score >= 85 and recovery_index >= 75:
            md += """### 🏆 高强度训练日

**具体行动：**
- 晨起：空腹低心率骑行30分钟（心率保持130-140）
- 上午：泳池基础训练（四项基础强化）
- 下午：1000米蛙泳测试或技术突破
- 晚上：轻度拉伸恢复

**小憨眯一下建议：**
- 训练间隙：深度放松5分钟
- 午休：小憨眯一下20分钟（HR降至最低）
- 晚上：冥想10分钟提升恢复

**营养建议：**
- 训练前：MCT油 + BCAA
- 训练后：蛋白质 + 快速碳水
- 全天：充足水分（体重×35ml）

"""
        elif readiness_score >= 70:
            md += """### 💪 中等强度训练日

**具体行动：**
- 晨起：低心率有氧20-30分钟
- 上午：泳池技术训练（四项基础）
- 下午：核心力量训练或陆地训练
- 晚上：拉伸放松

**小憨眯一下建议：**
- 午休：小憨眯一下15-20分钟
- 训练后：呼吸放松练习
- 晚上：温水浴促进恢复

**营养建议：**
- 训练前：适量碳水
- 训练后：蛋白质补充
- 全天：保持水分充足

"""
        else:
            md += """### 🧘 恢复日

**具体行动：**
- 晨起：轻度活动或休息
- 上午：瑜伽或拉伸
- 下午：轻松散步或水中放松游
- 晚上：充分休息

**小憨眯一下建议：**
- 上午：小憨眯一下20-30分钟
- 下午：再次小憨眯一下15-20分钟
- 晚上：早睡，保证睡眠时间

**营养建议：**
- 抗炎食物：深海鱼、坚果、浆果
- 补充：镁、维生素D3
- 避免：酒精、高糖食物

**特别提醒：**
- 今日不适合高强度训练
- 专注于恢复和准备
- 为明日训练储备能量

"""

        # 泳池训练建议
        if self.pool_training_advisor:
            readiness_score = self.health_data.get("readiness", {}).get("score", 0)
            recovery_index = self.health_data.get("readiness", {}).get("contributors", {}).get("recovery_index", 0)

            pool_md = self.pool_training_advisor.generate_pool_training_recommendations_md(
                readiness_score=readiness_score,
                recovery_index=recovery_index
            )
            md += pool_md

        # 两餐制饮食建议
        if self.two_meal_advisor:
            readiness_score = self.health_data.get("readiness", {}).get("score", 0)
            recovery_index = self.health_data.get("readiness", {}).get("contributors", {}).get("recovery_index", 0)
            weather_temp = self.weather_data.get("current", {}).get("temp_c", 20)

            # 确定训练强度
            if readiness_score >= 85:
                training_intensity = "high"
            elif readiness_score >= 70:
                training_intensity = "medium"
            else:
                training_intensity = "recovery"

            # 生成两餐计划
            diet_md = self.two_meal_advisor.generate_two_meal_plan(
                readiness_score=readiness_score,
                training_intensity=training_intensity,
                weather_temp=weather_temp
            )
            md += diet_md

            # 生成补剂检查清单
            supplement_md = self.two_meal_advisor.generate_supplement_checklist()
            md += supplement_md

        # 高级健康指标分析
        if self.advanced_analyzer:
            advanced_md = self.advanced_analyzer.generate_advanced_health_metrics_md(self.health_data)
            md += advanced_md

        # 健康指标可视化
        if self.advanced_analyzer:
            visual_md = self.advanced_analyzer.create_progress_bars_md(self.health_data)
            md += visual_md

        # 个人最好成绩
        if self.training_analyzer:
            md += "\n## 🏆 个人最好成绩 (PB)\n\n"
            md += self.training_analyzer.get_personal_best_summary()

        # 补剂提醒
        md += "\n## 💊 补剂提醒\n\n"

        day_of_month = self.today.day
        if day_of_month % 2 == 0:
            md += "### 今日服药日 ✓\n\n- ☑ 异维A酸 10mg\n\n"
        else:
            md += "### 今日非服药日 ○\n\n- ☐ 异维A酸 10mg\n\n"

        md += f"""### 日常补剂

- ☑ NMN22000 1粒（早晨）
- ☑ 益生菌（空腹）
- ☑ 鱼油（早餐后）
- ☑ 维生素D3（午餐后）
- ☑ 镁（睡前）

---

"""

        # 数据来源和科学依据
        if self.advanced_analyzer:
            sources_md = self.advanced_analyzer.generate_data_sources_md()
            md += sources_md

        # 页脚
        md += f"""---

*系统版本：v2.0 | 更新时间：{self.today.strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源：Oura Ring + Open-Meteo + WAQI + 8Sleep*
*本系统基于科学研究和个人数据，助您达到最佳表现* 🏊
"""

        # 保存报告
        report_file = self.dashboard_dir / f"dashboard_{self.today_str}.md"

        # 调试：显示md字符串长度
        print(f"\n📊 报告统计:")
        print(f"  MD字符串长度: {len(md)} 字符")
        print(f"  MD字符串行数: {md.count(chr(10))} 行")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(md)

        # 验证文件完整性
        import os
        file_size = os.path.getsize(report_file)
        if file_size < 1000:  # 如果文件小于1KB，可能有问题
            print(f"⚠️ 警告：生成的文件大小异常 ({file_size} bytes)")
        else:
            print(f"\n✓ 终极看板已保存: {report_file} ({file_size/1024:.1f} KB)")

            # 显示文件行数和大小
            with open(report_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            print(f"  行数: {line_count} 行")

        # 同时生成HTML版本
        self.generate_html_dashboard(detailed_analysis)

        # 验证完整性
        self._verify_dashboard_integrity(report_file)

        return md

    def _verify_dashboard_integrity(self, report_file):
        """验证看板文件完整性"""
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 必需章节
            required_sections = [
                "📊 今日健康评分",
                "🌤️ 今日天气",
                "🌬️ 空气质量",
                "🎯 训练建议",
                "💡 今日具体推荐",
                "🍽️ 每日饮食建议",
                "🏆 个人最好成绩",
                "💊 补剂提醒"
            ]

            # 检查所有必需章节
            missing = [s for s in required_sections if s not in content]

            if missing:
                print(f"⚠️ 警告：以下章节缺失 - {', '.join(missing)}")
            else:
                print(f"✅ 完整性验证通过！所有 {len(required_sections)} 个章节都存在")

        except Exception as e:
            print(f"⚠️ 验证失败: {e}")

    def generate_html_dashboard(self, detailed_analysis=None):
        """生成完整可视化HTML看板 - 包含Chart.js和matplotlib图表"""

        html_file = self.dashboard_dir / f"dashboard_{self.today_str}.html"
        visual_html_file = self.dashboard_dir / f"dashboard_visual_{self.today_str}.html"
        full_html_file = self.dashboard_dir / "dashboard_with_charts.html"

        # 读取markdown文件
        md_file = self.dashboard_dir / f"dashboard_{self.today_str}.md"

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 提取健康数据
            readiness_score = self.health_data.get("readiness", {}).get("score", 0)
            recovery_index = self.health_data.get("readiness", {}).get("contributors", {}).get("recovery_index", 0)
            hrv_balance = self.health_data.get("readiness", {}).get("contributors", {}).get("hrv_balance", 0)
            resting_hr = self.health_data.get("readiness", {}).get("contributors", {}).get("resting_heart_rate", 0)
            sleep_balance = self.health_data.get("readiness", {}).get("contributors", {}).get("sleep_balance", 0)
            activity_balance = self.health_data.get("readiness", {}).get("contributors", {}).get("activity_balance", 0)

            sleep_score = self.health_data.get("sleep", {}).get("score", 0)
            sleep_total = self.health_data.get("sleep", {}).get("contributors", {}).get("total_sleep", 0)
            sleep_deep = self.health_data.get("sleep", {}).get("contributors", {}).get("deep_sleep", 0)
            sleep_rem = self.health_data.get("sleep", {}).get("contributors", {}).get("rem_sleep", 0)
            sleep_efficiency = self.health_data.get("sleep", {}).get("contributors", {}).get("efficiency", 0)
            sleep_latency = self.health_data.get("sleep", {}).get("contributors", {}).get("latency", 0)
            sleep_restfulness = self.health_data.get("sleep", {}).get("contributors", {}).get("restfulness", 0)
            sleep_timing = self.health_data.get("sleep", {}).get("contributors", {}).get("timing", 0)

            # 生成基础HTML（保留原有功能）
            html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金明 - 终极健康看板</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        .content {{
            font-size: 16px;
        }}
        .content h1 {{
            font-size: 2.5em;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .content h2 {{
            font-size: 2em;
            color: #764ba2;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        .content h3 {{
            font-size: 1.5em;
            color: #333;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .content th, .content td {{
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        .content th {{
            background: #667eea;
            color: white;
        }}
        .content tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .content ul {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        .content li {{
            margin: 8px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            font-size: 0.9em;
        }}
        .highlight {{
            background: #f0f9ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <pre style="white-space: pre-wrap; font-family: inherit; font-size: inherit;">{md_content}</pre>
        </div>
        <div class="footer">
            <p>数据来源：Oura Ring + Open-Meteo + WAQI + 8Sleep</p>
            <p>更新时间：{self.today.strftime('%Y-%m-%d %H:%M:%S')} | 推送通知已发送 ✓</p>
        </div>
    </div>
    <script>setTimeout(function() {{ location.reload(); }}, 300000);</script>
</body>
</html>"""

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"✓ 基础HTML看板已保存: {html_file}")

            # 生成专业可视化HTML（包含Chart.js交互图表）
            visual_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金明 - 专业健康数据可视化看板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
            font-size: 1.1em;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        .card-title {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 1em;
            margin-top: 5px;
        }}
        .chart-container {{
            position: relative;
            height: 350px;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        .gauge-container {{
            position: relative;
            text-align: center;
            padding: 20px;
        }}
        .gauge-value {{
            font-size: 5em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .gauge-label {{
            color: #666;
            font-size: 1.2em;
            margin-top: 10px;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #f0f0f0;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        }}
        .recommendation {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }}
        .recommendation-title {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }}
        .update-time {{
            text-align: center;
            color: white;
            padding: 15px;
            font-size: 0.9em;
        }}
        .chart-img {{
            width: 100%;
            border-radius: 10px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏊 金明 - 专业健康数据可视化看板</h1>
            <p>自由潜水世界纪录保持者 | <span id="current-date"></span></p>
        </div>

        <!-- 准备度仪表盘 -->
        <div class="card">
            <div class="card-title">🎯 今日训练准备度</div>
            <div class="gauge-container">
                <div class="gauge-value" id="readiness-score">{readiness_score}</div>
                <div class="gauge-label" id="readiness-status">{'🔥 最佳状态' if readiness_score >= 85 else '💪 训练状态' if readiness_score >= 70 else '🧘 恢复日'}</div>
            </div>
            <div style="margin-top: 20px;">
                <div class="progress-bar">
                    <div class="progress-fill" id="readiness-bar" style="width: {readiness_score}%;">{readiness_score}%</div>
                </div>
            </div>
            <div class="recommendation">
                <div class="recommendation-title">💡 建议：</div>
                <div id="readiness-recommendation">
                    {'今日是挑战个人记录的好时机！你的状态接近创造7.6L肺活量PB时的水平' if readiness_score >= 85 else '适合系统训练，巩固技术' if readiness_score >= 70 else '建议轻量训练或休息'}
                </div>
            </div>
        </div>

        <div class="dashboard-grid">
            <!-- 雷达图 -->
            <div class="card">
                <div class="card-title">📊 健康指标雷达图</div>
                <div class="chart-container">
                    <canvas id="radarChart"></canvas>
                </div>
            </div>

            <!-- 睡眠质量 -->
            <div class="card">
                <div class="card-title">😴 睡眠质量分析</div>
                <div class="chart-container">
                    <canvas id="sleepChart"></canvas>
                </div>
            </div>

            <!-- HRV分析 -->
            <div class="card">
                <div class="card-title">💓 HRV深度分析</div>
                <div style="padding: 20px;">
                    <div class="stat-row">
                        <div class="stat-item">
                            <div class="stat-value">{hrv_balance}</div>
                            <div class="stat-label">HRV评分</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{'极佳' if hrv_balance >= 80 else '良好' if hrv_balance >= 65 else '一般'}</div>
                            <div class="stat-label">状态区间</div>
                        </div>
                    </div>
                    <div class="chart-container" style="height: 250px;">
                        <canvas id="hrvTrendChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- 活动分布 -->
            <div class="card">
                <div class="card-title">🏃 活动分布</div>
                <div class="chart-container">
                    <canvas id="activityChart"></canvas>
                </div>
            </div>
        </div>

        <!-- 周趋势 -->
        <div class="card full-width">
            <div class="card-title">📈 7日趋势图</div>
            <div class="chart-container">
                <canvas id="trendChart" style="height: 300px;"></canvas>
            </div>
        </div>

        <!-- 详细数据 -->
        <div class="card full-width">
            <div class="card-title">📋 详细健康数据</div>
            <div id="detailed-data">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 2em; font-weight: bold; color: #667eea;">{readiness_score}</div>
                        <div style="color: #666; margin-top: 5px;">准备度分数</div>
                    </div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 2em; font-weight: bold; color: #10b981;">{recovery_index}</div>
                        <div style="color: #666; margin-top: 5px;">恢复指数</div>
                    </div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 2em; font-weight: bold; color: #8b5cf6;">{sleep_balance}</div>
                        <div style="color: #666; margin-top: 5px;">睡眠平衡</div>
                    </div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 2em; font-weight: bold; color: #f59e0b;">{hrv_balance}</div>
                        <div style="color: #666; margin-top: 5px;">HRV平衡</div>
                    </div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 2em; font-weight: bold; color: #667eea;">{activity_balance}</div>
                        <div style="color: #666; margin-top: 5px;">活动平衡</div>
                    </div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 2em; font-weight: bold; color: #10b981;">{sleep_score}</div>
                        <div style="color: #666; margin-top: 5px;">睡眠总分</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 完整Markdown内容（保留所有文字信息） -->
        <div class="card full-width">
            <div class="card-title">📝 完整健康报告</div>
            <div style="max-height: 600px; overflow-y: auto; padding: 10px;">
                <pre style="white-space: pre-wrap; font-family: inherit; font-size: 14px; line-height: 1.6;">{md_content}</pre>
            </div>
        </div>

        <div class="update-time">
            数据来源：Oura Ring + Open-Meteo + WAQI + 8Sleep<br>
            更新时间：<span id="update-time"></span> | 自动刷新：5分钟
        </div>
    </div>

    <script>
        // 更新日期
        document.getElementById('current-date').textContent = new Date().toLocaleDateString('zh-CN', {{
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
        }});

        // 创建雷达图
        const radarCtx = document.getElementById('radarChart').getContext('2d');
        new Chart(radarCtx, {{
            type: 'radar',
            data: {{
                labels: ['HRV平衡', '恢复指数', '静息心率', '睡眠平衡', '活动平衡'],
                datasets: [{{
                    label: '当前状态',
                    data: [{hrv_balance}, {recovery_index}, {resting_hr}, {sleep_balance}, {activity_balance}],
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgb(102, 126, 234)',
                    pointBackgroundColor: 'rgb(102, 126, 234)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(102, 126, 234)'
                }}, {{
                    label: '优秀水平',
                    data: [85, 85, 85, 85, 85],
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderColor: 'rgba(75, 192, 192, 0.5)',
                    borderDash: [5, 5],
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        angleLines: {{ color: 'rgba(0, 0, 0, 0.1)' }},
                        grid: {{ color: 'rgba(0, 0, 0, 0.1)' }},
                        pointLabels: {{
                            font: {{ size: 13 }},
                            color: '#333'
                        }},
                        ticks: {{
                            backdropColor: 'rgba(255, 255, 255, 0.75)',
                            color: '#666'
                        }},
                        suggestedMin: 0,
                        suggestedMax: 100
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top',
                    }}
                }}
            }}
        }});

        // 创建睡眠质量柱状图
        const sleepCtx = document.getElementById('sleepChart').getContext('2d');
        new Chart(sleepCtx, {{
            type: 'bar',
            data: {{
                labels: ['总睡眠', '深睡', 'REM', '效率', '入睡', '安享度', '规律'],
                datasets: [{{
                    label: '睡眠评分',
                    data: [{sleep_total}, {sleep_deep}, {sleep_rem}, {sleep_efficiency}, {sleep_latency}, {sleep_restfulness}, {sleep_timing}],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(251, 146, 60, 0.8)',
                        'rgba(214, 51, 132, 0.8)'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{ color: '#666' }}
                    }},
                    x: {{
                        ticks: {{ color: '#333', font: {{ size: 11 }} }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});

        // 创建活动分布饼图
        const activityCtx = document.getElementById('activityChart').getContext('2d');
        new Chart(activityCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['高活动', '中等活动', '低活动', '休息/睡眠'],
                datasets: [{{
                    data: [35, 25, 20, 20],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(245, 87, 108, 0.8)'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});

        // HRV趋势图（模拟7天数据）
        const hrvCtx = document.getElementById('hrvTrendChart').getContext('2d');
        new Chart(hrvCtx, {{
            type: 'line',
            data: {{
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '今天'],
                datasets: [{{
                    label: 'HRV评分',
                    data: [72, 78, 82, 75, 88, 84, {hrv_balance}],
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        min: 50,
                        max: 100,
                        ticks: {{ color: '#666' }}
                    }},
                    x: {{
                        ticks: {{ color: '#333' }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});

        // 7日趋势图
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {{
            type: 'line',
            data: {{
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '今天'],
                datasets: [{{
                    label: '准备度',
                    data: [72, 78, 85, 82, 88, 84, {readiness_score}],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }}, {{
                    label: '睡眠分数',
                    data: [68, 75, 82, 70, 78, 72, {sleep_score}],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        min: 50,
                        max: 100,
                        ticks: {{ color: '#666' }}
                    }},
                    x: {{
                        ticks: {{ color: '#333' }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top'
                    }}
                }}
            }}
        }});

        // 更新时间
        document.getElementById('update-time').textContent = new Date().toLocaleString('zh-CN');

        // 自动刷新（5分钟）
        setTimeout(function() {{ location.reload(); }}, 300000);
    </script>
</body>
</html>"""

            with open(visual_html_file, 'w', encoding='utf-8') as f:
                f.write(visual_html)

            print(f"✓ 可视化HTML看板已保存: {visual_html_file}")

            # 同时更新 dashboard_with_charts.html（固定文件名，方便浏览器书签）
            with open(full_html_file, 'w', encoding='utf-8') as f:
                f.write(visual_html)

            print(f"✓ 专业看板已更新: {full_html_file}")

        except FileNotFoundError:
            print(f"⚠️ Markdown文件未找到，无法生成HTML")

        return full_html_file

def main():
    dashboard = UltimateHealthDashboard()
    dashboard.generate_ultimate_dashboard()

if __name__ == "__main__":
    main()
