#!/usr/bin/env python3
"""
金明训练日志管理系统
- 整合历史数据（800-2000天）
- 梳理每天训练内容
- 方便查找和查看
- 方便日常登记
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess


class TrainingLogManager:
    """训练日志管理器"""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.logs_dir = self.base_dir / "TrainingLogs"
        self.logs_dir.mkdir(exist_ok=True)

        # 数据文件
        self.log_file = self.logs_dir / "training_logs.json"
        self.index_file = self.logs_dir / "logs_index.json"
        self.stats_file = self.logs_dir / "training_stats.json"

        # 搜索历史数据文件
        self.historical_data_files = []
        self._find_historical_data()

        # 加载或初始化数据
        self.logs = self._load_logs()
        self.index = self._load_index()
        self.stats = self._load_stats()

    def _find_historical_data(self):
        """搜索历史训练数据文件"""
        print("🔍 搜索历史训练数据...")

        # 搜索Excel文件
        for excel_file in self.base_dir.rglob("*.xlsx"):
            if any(keyword in excel_file.name.lower()
                   for keyword in ['训练', 'training', '游泳', 'swim', '潜水', 'dive']):
                self.historical_data_files.append(excel_file)
                print(f"  ✓ 找到: {excel_file.name}")

        # 搜索Markdown日志
        for md_file in self.base_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 检查是否包含训练记录
                    if any(keyword in content for keyword in ['训练', '游泳', '蛙泳', '1000米']):
                        self.historical_data_files.append(md_file)
            except:
                pass

        print(f"✓ 共找到 {len(self.historical_data_files)} 个历史数据文件\n")

    def _load_logs(self) -> Dict:
        """加载训练日志"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"entries": []}

    def _load_index(self) -> Dict:
        """加载日志索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "by_date": {},
            "by_type": {},
            "by_location": {},
            "stats": {
                "total_days": 0,
                "total_sessions": 0,
                "earliest_date": None,
                "latest_date": None
            }
        }

    def _load_stats(self) -> Dict:
        """加载统计数据"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "personal_bests": {},
            "training_streaks": {},
            "averages": {}
        }

    def _save_logs(self):
        """保存训练日志"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=2)

    def _save_index(self):
        """保存索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _save_stats(self):
        """保存统计"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def add_entry(self, date: str, entry: Dict) -> bool:
        """添加训练日志"""
        try:
            # 标准化日期格式
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_str = date_obj.strftime("%Y-%m-%d")

            # 检查是否已存在
            if date_str in self.index["by_date"]:
                print(f"⚠️ 日期 {date_str} 的日志已存在")
                return False

            # 添加到日志
            entry["date"] = date_str
            entry["created_at"] = datetime.now().isoformat()
            self.logs["entries"].append(entry)

            # 更新索引
            self.index["by_date"][date_str] = len(self.logs["entries"]) - 1

            # 按类型索引
            training_type = entry.get("training_type", "未分类")
            if training_type not in self.index["by_type"]:
                self.index["by_type"][training_type] = []
            self.index["by_type"][training_type].append(date_str)

            # 按地点索引
            location = entry.get("location", "未知地点")
            if location not in self.index["by_location"]:
                self.index["by_location"][location] = []
            self.index["by_location"][location].append(date_str)

            # 更新统计
            self.index["stats"]["total_days"] = len(self.logs["entries"])
            self.index["stats"]["total_sessions"] += 1
            if self.index["stats"]["earliest_date"] is None or date_str < self.index["stats"]["earliest_date"]:
                self.index["stats"]["earliest_date"] = date_str
            if self.index["stats"]["latest_date"] is None or date_str > self.index["stats"]["latest_date"]:
                self.index["stats"]["latest_date"] = date_str

            # 保存
            self._save_logs()
            self._save_index()

            print(f"✓ 训练日志已添加：{date_str}")
            return True

        except Exception as e:
            print(f"⚠️ 添加日志失败：{e}")
            return False

    def search_logs(self, **kwargs) -> List[Dict]:
        """搜索训练日志

        参数：
            - date: 日期（YYYY-MM-DD）
            - date_range: 日期范围 (start_date, end_date)
            - training_type: 训练类型
            - location: 地点
            - content_contains: 内容包含关键词
        """
        results = []

        for entry in self.logs["entries"]:
            match = True

            # 日期筛选
            if "date" in kwargs:
                if entry["date"] != kwargs["date"]:
                    match = False

            # 日期范围筛选
            if "date_range" in kwargs and match:
                start, end = kwargs["date_range"]
                if not (start <= entry["date"] <= end):
                    match = False

            # 训练类型筛选
            if "training_type" in kwargs and match:
                if entry.get("training_type") != kwargs["training_type"]:
                    match = False

            # 地点筛选
            if "location" in kwargs and match:
                if entry.get("location") != kwargs["location"]:
                    match = False

            # 内容关键词筛选
            if "content_contains" in kwargs and match:
                content = json.dumps(entry, ensure_ascii=False)
                if kwargs["content_contains"] not in content:
                    match = False

            if match:
                results.append(entry)

        return results

    def get_logs_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """按日期范围获取日志"""
        return self.search_logs(date_range=(start_date, end_date))

    def get_recent_logs(self, days: int = 7) -> List[Dict]:
        """获取最近N天的日志"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_logs_by_date_range(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

    def get_log_by_date(self, date: str) -> Optional[Dict]:
        """按日期获取单条日志"""
        results = self.search_logs(date=date)
        return results[0] if results else None

    def generate_daily_report(self, date: str = None) -> str:
        """生成每日训练报告"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        log = self.get_log_by_date(date)

        if not log:
            return f"# {date} 训练日志\n\n暂无记录\n"

        md = f"""# {date} 训练日志

**训练类型：** {log.get('training_type', '未分类')}
**地点：** {log.get('location', '未知地点')}
**时长：** {log.get('duration', '未记录')}分钟

---

## 📋 训练内容

{log.get('content', '无详细内容')}

---

## 📊 数据记录

{self._format_training_data(log.get('data', {}))}

---

## 💡 训练总结

{log.get('summary', '无总结')}

---

## ⭐ 个人最好成绩

{self._format_personal_bests(log.get('personal_bests', {}))}

---

*记录时间：{log.get('created_at', '未知')}*
"""
        return md

    def _format_training_data(self, data: Dict) -> str:
        """格式化训练数据"""
        if not data:
            return "无数据记录"

        lines = []
        for key, value in data.items():
            lines.append(f"- **{key}：** {value}")

        return "\n".join(lines)

    def _format_personal_bests(self, pbs: Dict) -> str:
        """格式化个人最好成绩"""
        if not pbs:
            return "无PB记录"

        lines = []
        for event, record in pbs.items():
            lines.append(f"- **{event}：** {record}")

        return "\n".join(lines)

    def import_from_excel(self, excel_file: Path) -> int:
        """从Excel导入训练数据"""
        try:
            import pandas as pd

            print(f"📖 读取Excel文件：{excel_file.name}")
            df = pd.read_excel(excel_file)

            count = 0
            for _, row in df.iterrows():
                # 提取日期
                date_col = None
                for col in df.columns:
                    if '日期' in str(col) or 'date' in str(col).lower():
                        date_col = col
                        break

                if date_col is None:
                    continue

                try:
                    date = pd.to_datetime(row[date_col]).strftime("%Y-%m-%d")

                    # 构建日志条目
                    entry = {
                        "training_type": "泳池训练",
                        "location": "训练记录导入",
                        "duration": 0,
                        "content": str(row.to_dict()),
                        "data": {},
                        "summary": "从Excel导入"
                    }

                    if self.add_entry(date, entry):
                        count += 1

                except Exception as e:
                    continue

            print(f"✓ 从Excel导入 {count} 条记录\n")
            return count

        except ImportError:
            print("⚠️ 需要安装pandas：pip install pandas openpyxl")
            return 0
        except Exception as e:
            print(f"⚠️ Excel导入失败：{e}")
            return 0

    def import_from_markdown(self, md_file: Path) -> int:
        """从Markdown导入训练日志"""
        try:
            print(f"📖 读取Markdown文件：{md_file.name}")

            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 尝试提取日期
            date_pattern = r'(\d{4})[-.](\d{1,2})[-.](\d{1,2})'
            dates = re.findall(date_pattern, content)

            if not dates:
                print(f"  ⚠️ 未找到日期信息")
                return 0

            # 使用第一个日期作为日志日期
            year, month, day = dates[0]
            date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            entry = {
                "training_type": "历史记录",
                "location": "Markdown导入",
                "duration": 0,
                "content": content[:1000],  # 限制长度
                "data": {"source_file": str(md_file.name)},
                "summary": f"从 {md_file.name} 导入"
            }

            if self.add_entry(date, entry):
                print(f"✓ 从Markdown导入成功\n")
                return 1

            return 0

        except Exception as e:
            print(f"⚠️ Markdown导入失败：{e}")
            return 0

    def import_all_historical_data(self):
        """导入所有历史数据"""
        print("=" * 60)
        print("开始导入所有历史训练数据")
        print("=" * 60 + "\n")

        total_imported = 0

        for data_file in self.historical_data_files:
            if data_file.suffix == '.xlsx':
                count = self.import_from_excel(data_file)
                total_imported += count
            elif data_file.suffix == '.md':
                count = self.import_from_markdown(data_file)
                total_imported += count

        print("=" * 60)
        print(f"✓ 导入完成！共导入 {total_imported} 条历史记录")
        print(f"  总训练天数：{self.index['stats']['total_days']}")
        print(f"  最早日期：{self.index['stats']['earliest_date']}")
        print(f"  最近日期：{self.index['stats']['latest_date']}")
        print("=" * 60)

    def generate_statistics(self) -> str:
        """生成训练统计报告"""
        md = """# 训练统计报告

---

## 📊 总体统计

"""

        md += f"""**总训练天数：** {self.index['stats']['total_days']}天
**总训练次数：** {self.index['stats']['total_sessions']}次
**数据范围：** {self.index['stats']['earliest_date']} 至 {self.index['stats']['latest_date']}

---

## 🏋️‍♂️ 训练类型分布

"""

        for training_type, dates in self.index["by_type"].items():
            md += f"- **{training_type}：** {len(dates)}次\n"

        md += "\n---\n\n## 📍 训练地点分布\n\n"

        for location, dates in self.index["by_location"].items():
            md += f"- **{location}：** {len(dates)}次\n"

        return md

    def interactive_add_log(self):
        """交互式添加训练日志"""
        print("\n" + "=" * 60)
        print("📝 添加训练日志")
        print("=" * 60 + "\n")

        # 获取日期
        date_input = input("日期（YYYY-MM-DD，留空使用今天）：").strip()
        if not date_input:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                date = date_input
            except:
                print("⚠️ 日期格式错误，使用今天")
                date = datetime.now().strftime("%Y-%m-%d")

        # 获取训练类型
        print("\n训练类型：")
        print("1. 泳池训练（无蹼/单蹼/双蹼/静态闭气）")
        print("2. 1000米蛙泳")
        print("3. 陆地训练")
        print("4. 恢复训练")
        print("5. 其他")

        type_choice = input("选择（1-5）：").strip()
        type_map = {
            "1": "泳池训练（四项基础）",
            "2": "1000米蛙泳",
            "3": "陆地训练",
            "4": "恢复训练",
            "5": "其他"
        }
        training_type = type_map.get(type_choice, "泳池训练")

        # 获取地点
        location = input("\n训练地点（留空默认为"泳池"）：").strip()
        if not location:
            location = "泳池"

        # 获取训练内容
        print("\n请输入训练内容（输入空行结束）：")
        content_lines = []
        while True:
            line = input("> ")
            if not line:
                break
            content_lines.append(line)
        content = "\n".join(content_lines)

        # 获取训练数据
        print("\n训练数据（可选）：")
        print("格式：项目名=数值（例如：总时间=17分56秒）")
        print("输入空行跳过")

        data = {}
        while True:
            line = input("> ")
            if not line:
                break
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()

        # 构建日志条目
        entry = {
            "training_type": training_type,
            "location": location,
            "duration": 0,
            "content": content,
            "data": data,
            "summary": "手动记录"
        }

        # 添加到日志
        if self.add_entry(date, entry):
            print(f"\n✓ 训练日志已成功添加！")

            # 询问是否生成报告
            gen_report = input("\n是否生成今日训练报告？(y/n)：").strip().lower()
            if gen_report == 'y':
                report = self.generate_daily_report(date)
                print("\n" + report)

    def open_log_viewer(self):
        """打开日志查看器（在浏览器中）"""
        import webbrowser
        import tempfile

        # 生成HTML查看器
        html = self._generate_log_viewer_html()

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html)
            temp_file = f.name

        # 在浏览器中打开
        webbrowser.open(f'file://{temp_file}')
        print(f"✓ 日志查看器已在浏览器中打开")

    def _generate_log_viewer_html(self) -> str:
        """生成日志查看器HTML"""
        recent_logs = self.get_recent_logs(30)

        logs_html = ""
        for log in reversed(recent_logs):
            logs_html += f"""
            <div class="log-entry">
                <div class="log-date">{log['date']}</div>
                <div class="log-type">{log.get('training_type', '未分类')}</div>
                <div class="log-content">{log.get('content', '无内容')[:200]}...</div>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金明训练日志查看器</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .log-entry {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            background: #f9f9f9;
        }}
        .log-date {{
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .log-type {{
            color: #8b5cf6;
            margin-bottom: 10px;
        }}
        .log-content {{
            color: #333;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏊 金明训练日志查看器</h1>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{self.index['stats']['total_days']}</div>
                <div>总训练天数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.index['stats']['total_sessions']}</div>
                <div>总训练次数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(self.index['by_type'])}</div>
                <div>训练类型</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(self.index['by_location'])}</div>
                <div>训练地点</div>
            </div>
        </div>

        <h2>最近30天训练记录</h2>
        {logs_html}
    </div>
</body>
</html>"""

        return html

    def generate_markdown_report(self, output_file: Path = None):
        """生成Markdown训练报告"""
        if output_file is None:
            output_file = self.logs_dir / f"training_report_{datetime.now().strftime('%Y-%m-%d')}.md"

        md = self.generate_statistics()
        md += "\n---\n\n"
        md += "## 📝 最近训练记录\n\n"

        recent_logs = self.get_recent_logs(7)
        for log in reversed(recent_logs):
            md += f"### {log['date']} - {log.get('training_type', '未分类')}\n\n"
            md += f"{log.get('content', '无内容')}\n\n"
            if log.get('data'):
                md += "**数据：**\n"
                for key, value in log['data'].items():
                    md += f"- {key}: {value}\n"
                md += "\n"
            md += "---\n\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)

        print(f"✓ Markdown报告已生成：{output_file}")
        return output_file


def main():
    """主函数"""
    manager = TrainingLogManager()

    while True:
        print("\n" + "=" * 60)
        print("🏊 金明训练日志管理系统")
        print("=" * 60)
        print("\n请选择：")
        print("1. 添加训练日志")
        print("2. 查看训练日志")
        print("3. 搜索训练日志")
        print("4. 生成统计报告")
        print("5. 导入历史数据")
        print("6. 打开日志查看器（浏览器）")
        print("0. 退出")

        choice = input("\n请选择（0-6）：").strip()

        if choice == "1":
            manager.interactive_add_log()

        elif choice == "2":
            date = input("查看日期（YYYY-MM-DD，留空查看今天）：").strip()
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            report = manager.generate_daily_report(date)
            print("\n" + report)

        elif choice == "3":
            keyword = input("搜索关键词：").strip()
            results = manager.search_logs(content_contains=keyword)
            print(f"\n找到 {len(results)} 条匹配记录：")
            for log in results[:10]:  # 限制显示10条
                print(f"  {log['date']} - {log.get('training_type', '未分类')}")

        elif choice == "4":
            stats = manager.generate_statistics()
            print("\n" + stats)

        elif choice == "5":
            confirm = input("确定要导入所有历史数据吗？(y/n)：").strip().lower()
            if confirm == 'y':
                manager.import_all_historical_data()

        elif choice == "6":
            manager.open_log_viewer()

        elif choice == "0":
            print("\n再见！🏊")
            break

        else:
            print("\n⚠️ 无效选择，请重新输入")


if __name__ == "__main__":
    main()
