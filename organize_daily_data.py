#!/usr/bin/env python3
"""
将Oura Ring数据按日期重新组织到每日文件夹
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil

def organize_data_by_date():
    """按日期组织数据"""

    # 路径设置
    source_dir = Path("OuraData")
    target_dir = Path("OuraDataDaily")
    target_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("重组Oura Ring数据 - 按日期组织")
    print("=" * 60)

    # 读取所有数据
    with open(source_dir / "daily_readiness_2026-01-01_to_2026-01-31.json", 'r') as f:
        readiness_data = json.load(f)

    with open(source_dir / "daily_sleep_2026-01-01_to_2026-01-31.json", 'r') as f:
        sleep_data = json.load(f)

    with open(source_dir / "daily_activity_2026-01-01_to_2026-01-31.json", 'r') as f:
        activity_data = json.load(f)

    with open(source_dir / "heartrate_2026-01-24_to_2026-01-31.json", 'r') as f:
        heartrate_data = json.load(f)

    with open(source_dir / "sleep_timeseries_2026-01-24_to_2026-01-31.json", 'r') as f:
        sleep_ts_data = json.load(f)

    # 创建日期字典
    dates = set()
    for item in readiness_data.get('data', []):
        dates.add(item['day'])

    # 按日期组织
    for date in sorted(dates):
        date_dir = target_dir / date
        date_dir.mkdir(exist_ok=True)

        daily_data = {
            'date': date,
            'readiness': None,
            'sleep': None,
            'activity': None,
            'heartrate': [],
            'sleep_timeseries': []
        }

        # 查找当日的准备度数据
        for item in readiness_data.get('data', []):
            if item['day'] == date:
                daily_data['readiness'] = item
                break

        # 查找当日的睡眠数据
        for item in sleep_data.get('data', []):
            if item['day'] == date:
                daily_data['sleep'] = item
                break

        # 查找当日的活动数据
        for item in activity_data.get('data', []):
            if item['day'] == date:
                daily_data['activity'] = item
                break

        # 查找当日的心率数据（时间序列）
        if 'data' in heartrate_data:
            for item in heartrate_data['data']:
                item_date = item.get('timestamp', '')[:10]
                if item_date == date:
                    daily_data['heartrate'].append(item)

        # 查找当日的睡眠时间序列数据
        if 'data' in sleep_ts_data:
            for item in sleep_ts_data['data']:
                item_date = item.get('day', '')
                if item_date == date:
                    daily_data['sleep_timeseries'].append(item)

        # 保存当日数据
        daily_file = date_dir / f"daily_summary.json"
        with open(daily_file, 'w', encoding='utf-8') as f:
            json.dump(daily_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"✓ {date}: 数据已保存")

    print(f"\n✓ 完成！数据已组织到: {target_dir}")
    print(f"  共处理 {len(dates)} 天的数据")

    return target_dir

def analyze_today():
    """分析今天的数据"""

    target_dir = Path("OuraDataDaily")
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = target_dir / today

    if not today_dir.exists():
        # 尝试最近的一天
        dates = sorted([d.name for d in target_dir.iterdir() if d.is_dir()])
        if dates:
            today = dates[-1]
            today_dir = target_dir / today
        else:
            print("未找到数据")
            return None

    print(f"\n分析日期: {today}")
    print("=" * 60)

    # 读取今日数据
    with open(today_dir / "daily_summary.json", 'r') as f:
        data = json.load(f)

    return data, today

if __name__ == "__main__":
    organize_data_by_date()
    analyze_today()
