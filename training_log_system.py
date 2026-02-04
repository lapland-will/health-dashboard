#!/usr/bin/env python3
"""
训练日志管理系统
支持训练日志和肺活量数据的输入、存储、分析
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from collections import defaultdict


class TrainingLogSystem:
    """训练日志系统"""

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent
        else:
            base_dir = Path(base_dir)

        self.base_dir = base_dir
        self.logs_dir = base_dir / "TrainingLogs"
        self.data_file = self.logs_dir / "training_logs.json"
        self.lung_capacity_file = self.logs_dir / "lung_capacity.json"
        self.personal_best_file = self.logs_dir / "personal_best.json"

        # 创建目录
        self.logs_dir.mkdir(exist_ok=True)

        # 初始化数据
        self.logs = self._load_logs()
        self.lung_capacity = self._load_lung_capacity()
        self.personal_best = self._load_personal_best()

    def _load_logs(self):
        """加载训练日志"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"logs": [], "metadata": {"created": datetime.now().isoformat()}}

    def _load_lung_capacity(self):
        """加载肺活量数据"""
        if self.lung_capacity_file.exists():
            with open(self.lung_capacity_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"records": [], "pb": 7962}  # PB: 7962 ml

    def _load_personal_best(self):
        """加载个人最好成绩"""
        if self.personal_best_file.exists():
            with open(self.personal_best_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "DNF": {"distance": 212, "date": None, "location": None},
            "DYN": {"distance": 319, "date": None, "location": None},
            "DYNB": {"distance": 287, "date": None, "location": None},
            "STA": {"time": "9:08", "seconds": 548, "date": None, "location": None}  # 9分08秒 = 548秒
        }

    def _save_logs(self):
        """保存训练日志"""
        self.logs["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=2)

    def _save_lung_capacity(self):
        """保存肺活量数据"""
        with open(self.lung_capacity_file, 'w', encoding='utf-8') as f:
            json.dump(self.lung_capacity, f, ensure_ascii=False, indent=2)

    def _save_personal_best(self):
        """保存个人最好成绩"""
        with open(self.personal_best_file, 'w', encoding='utf-8') as f:
            json.dump(self.personal_best, f, ensure_ascii=False, indent=2)

    def add_training_log(self, date, training_type, content, metrics=None, notes=None):
        """添加训练日志

        Args:
            date: 日期 (YYYY-MM-DD)
            training_type: 训练类型 (泳池训练/陆地训练/休息日/比赛)
            content: 训练内容描述
            metrics: 指标字典 {'distance': 米, 'time': 秒, 'attempts': 次数}
            notes: 备注
        """
        log = {
            "date": date,
            "training_type": training_type,
            "content": content,
            "metrics": metrics or {},
            "notes": notes or "",
            "created_at": datetime.now().isoformat()
        }

        self.logs["logs"].append(log)
        self._save_logs()
        return log

    def add_lung_capacity(self, date, measurements, notes=None):
        """添加肺活量测量记录

        Args:
            date: 日期 (YYYY-MM-DD)
            measurements: 测量值列表 [6428, 6462, 6632]
            notes: 备注
        """
        # 过滤掉0值
        valid_measurements = [m for m in measurements if m and m > 0]

        if not valid_measurements:
            return None

        max_today = max(valid_measurements)

        record = {
            "date": date,
            "measurements": valid_measurements,
            "max_today": max_today,
            "notes": notes or "",
            "created_at": datetime.now().isoformat()
        }

        self.lung_capacity["records"].append(record)

        # 更新PB
        if max_today > self.lung_capacity["pb"]:
            self.lung_capacity["pb"] = max_today

        self._save_lung_capacity()
        return record

    def update_personal_best(self, event, value, date=None, location=None):
        """更新个人最好成绩

        Args:
            event: 项目 (DNF/DYN/DYNB/STA)
            value: 值 (米数或时间字符串"9:08")
            date: 日期
            location: 地点
        """
        if event not in self.personal_best:
            return False

        if event == "STA":
            # 转换时间字符串为秒
            if isinstance(value, str):
                parts = value.split(":")
                if len(parts) == 2:
                    minutes, seconds = int(parts[0]), int(parts[1])
                    value_seconds = minutes * 60 + seconds
                else:
                    value_seconds = int(value)
            else:
                value_seconds = int(value)
                value = f"{value_seconds // 60}:{value_seconds % 60:02d}"

            self.personal_best[event] = {
                "time": value,
                "seconds": value_seconds,
                "date": date,
                "location": location
            }
        else:
            # DNF, DYN, DYNB - 距离项目
            self.personal_best[event] = {
                "distance": int(value),
                "date": date,
                "location": location
            }

        self._save_personal_best()
        return True

    def get_logs_by_date_range(self, start_date, end_date):
        """按日期范围获取日志"""
        logs = []
        for log in self.logs["logs"]:
            if start_date <= log["date"] <= end_date:
                logs.append(log)
        return sorted(logs, key=lambda x: x["date"], reverse=True)

    def get_logs_by_month(self, year, month):
        """按月获取日志"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        return self.get_logs_by_date_range(start_date, end_date)

    def search_logs(self, keyword):
        """搜索日志"""
        results = []
        keyword_lower = keyword.lower()

        for log in self.logs["logs"]:
            # 搜索内容、类型、备注
            if (keyword_lower in log["content"].lower() or
                keyword_lower in log["training_type"].lower() or
                keyword_lower in log["notes"].lower()):
                results.append(log)

        return sorted(results, key=lambda x: x["date"], reverse=True)

    def get_statistics(self, days=30):
        """获取统计数据

        Args:
            days: 统计最近多少天
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        recent_logs = [
            log for log in self.logs["logs"]
            if datetime.fromisoformat(log["date"]) >= start_date
        ]

        # 训练类型统计
        training_types = defaultdict(int)
        for log in recent_logs:
            training_types[log["training_type"]] += 1

        # 肺活量趋势
        lung_records = [
            r for r in self.lung_capacity["records"]
            if datetime.fromisoformat(r["date"]) >= start_date
        ]

        lung_values = [r["max_today"] for r in lung_records] if lung_records else []

        return {
            "total_logs": len(recent_logs),
            "training_types": dict(training_types),
            "lung_capacity_records": len(lung_records),
            "lung_capacity_avg": sum(lung_values) / len(lung_values) if lung_values else 0,
            "lung_capacity_max": max(lung_values) if lung_values else 0,
            "lung_capacity_trend": lung_values[-7:] if len(lung_values) >= 7 else lung_values
        }

    def get_lung_capacity_trend(self, days=30):
        """获取肺活量趋势"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        records = [
            r for r in self.lung_capacity["records"]
            if datetime.fromisoformat(r["date"]) >= start_date
        ]

        return sorted(records, key=lambda x: x["date"])

    def import_from_excel(self, excel_path):
        """从Excel导入肺活量数据"""
        try:
            df = pd.read_excel(excel_path)

            records = []
            for _, row in df.iterrows():
                # 尝试解析日期
                date = None
                for col in df.columns:
                    if '日期' in str(col) or 'date' in str(col).lower():
                        date_val = row[col]
                        if pd.notna(date_val):
                            if isinstance(date_val, str):
                                date = date_val
                            else:
                                date = str(date_val.date())
                            break

                if date and '2023' in date or '2024' in date or '2025' in date or '2026' in date:
                    # 提取肺活量测量值
                    measurements = []
                    for col in df.columns:
                        if '肺活量' in str(col):
                            val = row[col]
                            if pd.notna(val) and val > 0:
                                try:
                                    measurements.append(int(val))
                                except:
                                    pass

                    if measurements:
                        records.append({
                            "date": date,
                            "measurements": measurements,
                            "max_today": max(measurements) if measurements else 0,
                            "notes": "",
                            "imported": True
                        })

            return records

        except Exception as e:
            print(f"Error importing Excel: {e}")
            return []

    def export_to_json(self, output_path=None):
        """导出所有数据为JSON"""
        if output_path is None:
            output_path = self.logs_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            "training_logs": self.logs,
            "lung_capacity": self.lung_capacity,
            "personal_best": self.personal_best,
            "exported_at": datetime.now().isoformat()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_path


def main():
    """测试函数"""
    system = TrainingLogSystem()

    # 导入肺活量数据
    excel_files = [
        '/Users/williamjoy/Desktop/个人投资/肺活量测量表.xlsx',
        '/Users/williamjoy/Desktop/金明自由潜/肺活量测量表.xlsx'
    ]

    for excel_file in excel_files:
        if os.path.exists(excel_file):
            print(f"导入: {excel_file}")
            records = system.import_from_excel(excel_file)
            print(f"  找到 {len(records)} 条记录")

            for record in records:
                system.add_lung_capacity(
                    date=record["date"],
                    measurements=record["measurements"],
                    notes=record.get("notes", "")
                )

    # 打印统计
    stats = system.get_statistics(days=365)
    print(f"\n肺活量记录总数: {stats['lung_capacity_records']}")
    print(f"肺活量PB: {system.lung_capacity['pb']} ml")
    print(f"最近30天平均: {stats['lung_capacity_avg']:.0f} ml")

    # 打印个人最好成绩
    print(f"\n个人最好成绩:")
    for event, data in system.personal_best.items():
        if event == "STA":
            print(f"  {event}: {data['time']} ({data['seconds']}秒)")
        else:
            print(f"  {event}: {data['distance']}米")


if __name__ == "__main__":
    main()
