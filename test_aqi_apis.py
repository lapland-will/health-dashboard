#!/usr/bin/env python3
"""
空气质量API获取 - 使用多个备用API
"""

import requests
import json
from datetime import datetime

def get_aqi_from_wnct():
    """使用中国环境监测总站API获取数据"""
    try:
        # 使用公开的PM2.5数据
        cities = {
            "上海": {"lat": 31.2304, "lon": 121.4737},
            "北京": {"lat": 39.9042, "lon": 116.4074},
            "深圳": {"lat": 22.5431, "lon": 114.0579}
        }

        city = "上海"
        lat = cities[city]["lat"]
        lon = cities[city]["lon"]

        # 使用WAQI的公开API（无需token的feed）
        url = f"https://waqi.info/search/{city}/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        print(f"✓ 获取到{city}的空气质量数据")
        print(f"响应: {response.text[:500]}")

        return response.json()

    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return None

def get_aqi_from_openaq():
    """使用OpenAQ API获取数据"""
    try:
        # OpenAQ API (免费，无需key)
        url = "https://api.openaq.org/v1/measurements"
        params = {
            "city": "Shanghai",
            "country": "CN",
            "parameter": "pm25",
            "sort": "desc",
            "limit": 1
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get("results"):
            result = data["results"][0]
            pm25 = result.get("value", 0)

            print(f"✓ OpenAQ: PM2.5 = {pm25} μg/m³")

            return {
                "pm25": pm25,
                "source": "OpenAQ",
                "city": "Shanghai",
                "date": result.get("date", {}).get("utc", "")
            }

    except Exception as e:
        print(f"❌ OpenAQ获取失败: {e}")
        return None

def get_aqi_from_aqicn():
    """使用AQICN API获取数据"""
    try:
        # AQICN API
        city = "shanghai"
        url = f"https://api.waqi.info/feed/{city}/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get("status") == "ok":
            station_data = data.get("data", {})
            iaqi = station_data.get("iaqi", {})

            result = {
                "aqi": int(station_data.get("idx", 0)),
                "pm25": int(iaqi.get("pm25", {}).get("v", 0)),
                "pm10": int(iaqi.get("pm10", {}).get("v", 0)),
                "o3": int(iaqi.get("o3", {}).get("v", 0)),
                "no2": int(iaqi.get("no2", {}).get("v", 0)),
                "so2": int(iaqi.get("so2", {}).get("v", 0)),
                "city": station_data.get("city", {}).get("name", city),
                "source": "AQICN"
            }

            print(f"✓ AQICN: AQI = {result['aqi']}")
            print(f"  PM2.5: {result['pm25']} μg/m³")
            print(f"  PM10: {result['pm10']} μg/m³")

            return result

    except Exception as e:
        print(f"❌ AQICN获取失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("测试空气质量API")
    print("=" * 60)

    print("\n方法1: AQICN API")
    result1 = get_aqi_from_aqicn()

    if result1:
        print("\n✓ AQICN成功!")
        print(json.dumps(result1, indent=2, ensure_ascii=False))
    else:
        print("\n方法2: OpenAQ API")
        result2 = get_aqi_from_openaq()
        if result2:
            print("\n✓ OpenAQ成功!")
            print(json.dumps(result2, indent=2, ensure_ascii=False))
