#!/usr/bin/env python3
"""
Oura Ring数据同步脚本
用于从Oura Ring API V2获取健康数据并保存到本地
"""

import requests
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import os

class OuraRingDataSync:
    """Oura Ring数据同步类"""

    def __init__(self, access_token=None):
        """
        初始化
        :param access_token: Oura API访问令牌（Personal Access Token）
        """
        self.access_token = access_token or os.getenv('OURA_ACCESS_TOKEN')
        self.base_url = "https://api.ouraring.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        self.data_dir = Path(__file__).parent / "OuraData"
        self.data_dir.mkdir(exist_ok=True)

    def _make_request(self, endpoint, params=None):
        """发送API请求"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_daily_sleep(self, start_date=None, end_date=None):
        """
        获取每日睡眠数据
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "start_date": start_date,
            "end_date": end_date
        }

        data = self._make_request("usercollection/daily_sleep", params)
        if data:
            self._save_data(data, "daily_sleep", start_date, end_date)
        return data

    def get_daily_activity(self, start_date=None, end_date=None):
        """
        获取每日活动数据
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "start_date": start_date,
            "end_date": end_date
        }

        data = self._make_request("usercollection/daily_activity", params)
        if data:
            self._save_data(data, "daily_activity", start_date, end_date)
        return data

    def get_daily_readiness(self, start_date=None, end_date=None):
        """
        获取每日准备度数据
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "start_date": start_date,
            "end_date": end_date
        }

        data = self._make_request("usercollection/daily_readiness", params)
        if data:
            self._save_data(data, "daily_readiness", start_date, end_date)
        return data

    def get_heart_rate(self, start_date=None, end_date=None):
        """
        获取心率数据
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "start_datetime": f"{start_date}T00:00:00Z",
            "end_datetime": f"{end_date}T23:59:59Z"
        }

        data = self._make_request("usercollection/heartrate", params)
        if data:
            self._save_data(data, "heartrate", start_date, end_date)
        return data

    def get_sleep_time_series(self, start_date=None, end_date=None):
        """
        获取睡眠时间序列数据
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "start_datetime": f"{start_date}T00:00:00Z",
            "end_datetime": f"{end_date}T23:59:59Z"
        }

        data = self._make_request("usercollection/sleep", params)
        if data:
            self._save_data(data, "sleep_timeseries", start_date, end_date)
        return data

    def _save_data(self, data, data_type, start_date, end_date):
        """保存数据到文件"""
        # 保存为JSON
        json_file = self.data_dir / f"{data_type}_{start_date}_to_{end_date}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ 数据已保存: {json_file}")

        # 如果有数据，也保存为CSV格式
        if 'data' in data and len(data['data']) > 0:
            csv_file = self.data_dir / f"{data_type}_{start_date}_to_{end_date}.csv"
            self._save_csv(data['data'], csv_file)

    def _save_csv(self, data, csv_file):
        """保存为CSV格式"""
        if not data:
            return

        # 展开嵌套数据
        flat_data = []
        for item in data:
            flat_item = self._flatten_dict(item)
            flat_data.append(flat_item)

        if flat_data:
            keys = flat_data[0].keys()
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(flat_data)
            print(f"✓ CSV已保存: {csv_file}")

    def _flatten_dict(self, d, parent_key='', sep='_'):
        """展开嵌套字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # 对于列表，保存为JSON字符串
                items.append((new_key, json.dumps(v) if v else ''))
            else:
                items.append((new_key, v))
        return dict(items)

    def sync_all(self, days=30):
        """
        同步所有数据
        :param days: 获取最近几天的数据
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        print(f"开始同步Oura Ring数据 ({start_date} 到 {end_date})")
        print("=" * 60)

        # 获取各类数据
        print("\n1. 获取每日睡眠数据...")
        self.get_daily_sleep(start_date, end_date)

        print("\n2. 获取每日活动数据...")
        self.get_daily_activity(start_date, end_date)

        print("\n3. 获取每日准备度数据...")
        self.get_daily_readiness(start_date, end_date)

        print("\n4. 获取心率数据（最近7天）...")
        self.get_heart_rate(
            (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            end_date
        )

        print("\n5. 获取睡眠时间序列数据（最近7天）...")
        self.get_sleep_time_series(
            (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            end_date
        )

        print("\n" + "=" * 60)
        print("✓ 所有数据同步完成！")
        print(f"数据保存在: {self.data_dir}")


def main():
    """主函数"""
    print("Oura Ring数据同步工具")
    print("=" * 60)

    # 检查环境变量
    access_token = os.getenv('OURA_ACCESS_TOKEN')
    if not access_token:
        print("\n⚠️ 未找到OURA_ACCESS_TOKEN环境变量")
        print("\n获取Personal Access Token的步骤：")
        print("1. 访问: https://cloud.ouraring.com/personal-access-tokens")
        print("2. 创建一个新的Personal Access Token")
        print("3. 设置环境变量: export OURA_ACCESS_TOKEN='your_token_here'")
        print("\n或者在运行时手动输入token")

        access_token = input("\n请输入您的Oura Personal Access Token: ").strip()
        if not access_token:
            print("未提供token，退出。")
            return

    # 创建同步对象
    sync = OuraRingDataSync(access_token)

    # 同步数据
    try:
        days = input("\n请输入要获取的天数 (默认30天): ").strip()
        days = int(days) if days else 30
        sync.sync_all(days=days)
    except ValueError:
        print("输入无效，使用默认30天")
        sync.sync_all(days=30)
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
