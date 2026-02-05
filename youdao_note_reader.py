#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有道云笔记读取器 - 自动识别昨天的训练日志

功能：
1. 从有道云笔记导出的markdown文件中读取训练记录
2. 识别昨天的训练日志
3. 提取训练内容（日期、类型、时长、强度、主观感受）
4. 自动更新到训练日志系统
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

class YoudaoNoteReader:
    """有道云笔记读取器"""

    def __init__(self, note_export_path=None):
        """
        初始化有道云笔记读取器

        Args:
            note_export_path: 有道云笔记导出的文件夹路径
        """
        self.note_export_path = note_export_path or self._find_youdao_notes_path()
        self.training_logs = []

    def _find_youdao_notes_path(self):
        """自动查找有道云笔记导出路径"""
        # 常见的有道云笔记导出路径
        possible_paths = [
            os.path.expanduser("~/Documents/有道云笔记"),
            os.path.expanduser("~/Documents/YoudaoNotes"),
            os.path.expanduser("~/Desktop/有道云笔记导出"),
            os.path.expanduser("~/Desktop/YoudaoNotes"),
            "/Users/williamjoy/Documents/有道云笔记",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ 找到有道云笔记路径: {path}")
                return path

        print("⚠️ 未找到有道云笔记路径，请手动指定")
        return None

    def read_yesterday_training_log(self):
        """读取昨天的训练日志"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"📅 正在查找 {yesterday} 的训练记录...")

        if not self.note_export_path:
            print("❌ 有道云笔记路径未配置")
            return []

        # 搜索所有markdown文件
        all_notes = self._find_all_markdown_files()
        print(f"📄 找到 {len(all_notes)} 个markdown文件")

        # 查找昨天的训练记录
        yesterday_logs = []

        for note_file in all_notes:
            logs = self._extract_training_from_file(note_file, yesterday)
            if logs:
                yesterday_logs.extend(logs)

        print(f"✅ 找到 {len(yesterday_logs)} 条昨天的训练记录")
        return yesterday_logs

    def _find_all_markdown_files(self):
        """查找所有markdown文件"""
        if not self.note_export_path or not os.path.exists(self.note_export_path):
            return []

        markdown_files = []
        for root, dirs, files in os.walk(self.note_export_path):
            for file in files:
                if file.endswith(('.md', '.markdown')):
                    markdown_files.append(os.path.join(root, file))

        return markdown_files

    def _extract_training_from_file(self, file_path, target_date):
        """从文件中提取指定日期的训练记录"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找目标日期的训练记录
            # 支持多种日期格式
            date_patterns = [
                rf'{target_date}',  # 2026-02-04
                rf'{target_date[5:]}月{target_date[8:]}日',  # 02月04日
                rf'{target_date[5:]}月{int(target_date[8:]):d}日',  # 02月4日
            ]

            logs = []

            for pattern in date_patterns:
                if re.search(pattern, content):
                    # 找到匹配的日期，提取训练内容
                    training_data = self._parse_training_content(content, target_date)
                    if training_data:
                        logs.append(training_data)

            return logs

        except Exception as e:
            print(f"⚠️ 读取文件失败 {file_path}: {e}")
            return []

    def _parse_training_content(self, content, date):
        """解析训练内容"""
        training_data = {
            'date': date,
            'training_type': [],
            'duration': None,
            'intensity': None,
            'heart_rate': None,
            'spo2': None,
            'subjective_feeling': None,
            'notes': [],
            'raw_content': content
        }

        # 提取训练类型
        type_keywords = {
            '无蹼': 'DNF',
            '单蹼': '单蹼',
            '双蹼': 'DYNB',
            '静态闭气': 'STA',
            '蛙泳': '蛙泳',
            '陆地训练': '陆地训练',
            '瑜伽': '瑜伽',
            '骑行': '骑行',
            '跑步': '跑步',
            '拉伸': '拉伸'
        }

        for keyword, type_name in type_keywords.items():
            if keyword in content:
                if type_name not in training_data['training_type']:
                    training_data['training_type'].append(type_name)

        # 提取时长（例如：2小时、120分钟、2h）
        duration_patterns = [
            r'(\d+)\s*小时',
            r'(\d+)\s*分钟',
            r'(\d+)\s*h',
            r'(\d+)\s*min'
        ]

        for pattern in duration_patterns:
            matches = re.findall(pattern, content)
            if matches:
                # 取第一个匹配的时长
                duration_value = int(matches[0])
                if '小时' in pattern or 'h' in pattern:
                    duration_value *= 60
                training_data['duration'] = duration_value
                break

        # 提取强度
        intensity_keywords = ['高强度', '中等强度', '低强度', '轻松', '恢复']
        for keyword in intensity_keywords:
            if keyword in content:
                intensity_map = {
                    '高强度': 'high',
                    '中等强度': 'medium',
                    '低强度': 'low',
                    '轻松': 'low',
                    '恢复': 'recovery'
                }
                training_data['intensity'] = intensity_map.get(keyword, 'medium')
                break

        # 提取心率（例如：心率150bpm、HR: 150）
        heart_rate_patterns = [
            r'心率\s*(\d+)',
            r'HR[:\s]*(\d+)',
            r'(\d+)\s*bpm'
        ]

        for pattern in heart_rate_patterns:
            match = re.search(pattern, content)
            if match:
                training_data['heart_rate'] = int(match.group(1))
                break

        # 提取血氧（例如：血氧98%、SpO2: 98）
        spo2_patterns = [
            r'血氧\s*(\d+)',
            r'SpO2[:\s]*(\d+)'
        ]

        for pattern in spo2_patterns:
            match = re.search(pattern, content)
            if match:
                training_data['spo2'] = int(match.group(1))
                break

        # 提取主观感受
        feeling_keywords = {
            '很好': 5,
            '好': 4,
            '一般': 3,
            '差': 2,
            '很差': 1,
            '疲劳': 2,
            '轻松': 4,
            '状态佳': 5
        }

        for keyword, score in feeling_keywords.items():
            if keyword in content:
                training_data['subjective_feeling'] = score
                break

        # 提取笔记内容（去除日期行，保留实际内容）
        lines = content.split('\n')
        notes = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and target_date not in line:
                notes.append(line)

        training_data['notes'] = '\n'.join(notes[:10])  # 只取前10行作为笔记

        return training_data

    def save_to_training_log_system(self, logs):
        """保存到训练日志系统"""
        if not logs:
            print("⚠️ 没有训练记录需要保存")
            return

        # 读取现有训练日志
        log_file = "TrainingLogs/training_logs.json"

        existing_logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                existing_logs = json.load(f)

        # 添加新的训练记录
        for log in logs:
            # 检查是否已存在该日期的记录
            date_exists = any(
                existing_log.get('date') == log['date']
                for existing_log in existing_logs
            )

            if not date_exists:
                existing_logs.append(log)
                print(f"✅ 添加训练记录: {log['date']} - {', '.join(log['training_type'])}")
            else:
                print(f"⚠️ 日期 {log['date']} 的记录已存在，跳过")

        # 保存更新后的日志
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, ensure_ascii=False, indent=2)

        print(f"✅ 训练日志已更新，共 {len(existing_logs)} 条记录")

    def print_summary(self, logs):
        """打印训练记录摘要"""
        if not logs:
            print("📋 昨天没有找到训练记录")
            return

        print("\n" + "="*50)
        print("📋 昨天的训练记录摘要")
        print("="*50)

        for i, log in enumerate(logs, 1):
            print(f"\n记录 {i}:")
            print(f"  日期: {log['date']}")
            print(f"  训练类型: {', '.join(log['training_type'])}")
            if log['duration']:
                print(f"  时长: {log['duration']} 分钟")
            if log['intensity']:
                print(f"  强度: {log['intensity']}")
            if log['heart_rate']:
                print(f"  心率: {log['heart_rate']} bpm")
            if log['spo2']:
                print(f"  血氧: {log['spo2']}%")
            if log['subjective_feeling']:
                print(f"  主观感受: {log['subjective_feeling']}/5")

        print("\n" + "="*50)


def main():
    """主函数 - 测试和使用"""
    print("🔍 有道云笔记训练日志读取器")
    print("="*50)

    # 创建读取器
    reader = YoudaoNoteReader()

    # 读取昨天的训练日志
    yesterday_logs = reader.read_yesterday_training_log()

    # 打印摘要
    reader.print_summary(yesterday_logs)

    # 保存到训练日志系统
    if yesterday_logs:
        reader.save_to_training_log_system(yesterday_logs)

    return yesterday_logs


if __name__ == "__main__":
    main()
