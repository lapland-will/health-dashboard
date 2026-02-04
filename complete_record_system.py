#!/usr/bin/env python3
"""
金明 - 完整记录管理系统
- 查看训练记录和健康记录
- 方便查找和搜索
- 登记新记录
- 每3小时自动更新
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time


class RecordManagementSystem:
    """完整记录管理系统"""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.reports_dir = self.base_dir / "DailyReports"
        self.training_logs_dir = self.base_dir / "TrainingLogs"
        self.records_db = self.base_dir / "records_database.json"

        # 确保目录存在
        self.reports_dir.mkdir(exist_ok=True)
        self.training_logs_dir.mkdir(exist_ok=True)

        # 加载或初始化数据库
        self.records = self._load_records()

    def _load_records(self):
        """加载记录数据库"""
        if self.records_db.exists():
            with open(self.records_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"daily_reports": {}, "training_logs": {}}

    def _save_records(self):
        """保存记录数据库"""
        with open(self.records_db, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def scan_all_reports(self):
        """扫描所有报告文件"""
        print("📂 扫描所有报告文件...")

        # 扫描每日报告
        for report_file in self.reports_dir.glob("dashboard_*.md"):
            date_str = report_file.stem.replace("dashboard_", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                with open(report_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.records["daily_reports"][date_str] = {
                    "file": str(report_file),
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "content": content,
                    "size": len(content),
                    "lines": content.count('\n')
                }
            except:
                continue

        # 扫描训练日志
        for log_file in self.training_logs_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    for entry in logs.get("entries", []):
                        date_str = entry["date"]
                        self.records["training_logs"][date_str] = entry
            except:
                continue

        self._save_records()
        print(f"✓ 扫描完成：")
        print(f"  - 每日报告：{len(self.records['daily_reports'])} 天")
        print(f"  - 训练日志：{len(self.records['training_logs'])} 条")

    def generate_records_viewer_html(self):
        """生成记录查看器HTML"""

        # 获取最近的记录
        recent_reports = sorted(
            self.records["daily_reports"].items(),
            key=lambda x: x[0],
            reverse=True
        )[:30]

        recent_logs = sorted(
            self.records["training_logs"].items(),
            key=lambda x: x[0],
            reverse=True
        )[:30]

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金明 - 完整记录管理系统</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
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
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .search-box {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        .search-box input {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            margin-top: 10px;
        }}
        .search-box button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }}
        .search-box button:hover {{
            opacity: 0.9;
        }}
        .tabs {{
            background: white;
            border-radius: 15px;
            padding: 10px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            display: flex;
            gap: 10px;
        }}
        .tab {{
            flex: 1;
            padding: 15px;
            background: #f0f0f0;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
        }}
        .tab.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .tab-content {{
            display: none;
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }}
        .tab-content.active {{
            display: block;
        }}
        .record-card {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            background: #f9f9f9;
        }}
        .record-date {{
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .record-summary {{
            color: #666;
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        .record-detail {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s;
        }}
        .record-detail.expanded {{
            max-height: 2000px;
        }}
        .expand-btn {{
            background: none;
            border: 1px solid #667eea;
            color: #667eea;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }}
        .expand-btn:hover {{
            background: #667eea;
            color: white;
        }}
        .add-form {{
            display: none;
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        .add-form.active {{
            display: block;
        }}
        .form-group {{
            margin-bottom: 15px;
        }}
        .form-group label {{
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }}
        .form-group input,
        .form-group textarea,
        .form-group select {{
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
        }}
        .form-group textarea {{
            min-height: 100px;
            resize: vertical;
        }}
        .submit-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
        }}
        .submit-btn:hover {{
            opacity: 0.9;
        }}
        .results {{
            margin-top: 15px;
        }}
        .result-item {{
            padding: 10px;
            margin-bottom: 5px;
            background: #f0f0f0;
            border-radius: 8px;
            cursor: pointer;
        }}
        .result-item:hover {{
            background: #e0e0e0;
        }}
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
        .update-info {{
            text-align: center;
            color: white;
            padding: 15px;
            font-size: 0.9em;
        }}
        .quick-links {{
            background: white;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        .quick-links a {{
            display: inline-block;
            margin: 5px 10px;
            padding: 8px 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏊 金明 - 完整记录管理系统</h1>
            <p>查看训练记录 + 健康记录 | 登记新记录 | 每3小时自动更新</p>

            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(self.records["daily_reports"])}</div>
                    <div class="stat-label">每日报告</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(self.records["training_logs"])}</div>
                    <div class="stat-label">训练日志</div>
                </div>
                <div class="stat">
                    <div class="stat-value">30</div>
                    <div class="stat-label">最近天数</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{datetime.now().strftime("%H:%M")}</div>
                    <div class="stat-label">更新时间</div>
                </div>
            </div>
        </div>

        <!-- 快速链接 -->
        <div class="quick-links">
            <a href="#" onclick="openAddForm('health')">➕ 添加健康记录</a>
            <a href="#" onclick="openAddForm('training')">➕ 添加训练记录</a>
            <a href="super_dashboard.html" target="_blank">📊 打开今日看板</a>
            <a href="#" onclick="location.reload()">🔄 刷新页面</a>
        </div>

        <!-- 搜索框 -->
        <div class="search-box">
            <h3 style="color: #667eea;">🔍 搜索记录</h3>
            <input type="text" id="searchInput" placeholder="输入关键词搜索（如：蛙泳、PB、训练等）...">
            <button onclick="searchRecords()">🔍 搜索</button>
            <div id="searchResults" class="results"></div>
        </div>

        <!-- 标签页 -->
        <div class="tabs">
            <button class="tab active" onclick="switchTab('reports')">📋 每日报告</button>
            <button class="tab" onclick="switchTab('training')">🏋️ 训练日志</button>
            <button class="tab" onclick="switchTab('charts')">📊 数据分析</button>
            <button class="tab" onclick="switchTab('add')">➕ 添加记录</button>
        </div>

        <!-- 每日报告标签页 -->
        <div id="reports" class="tab-content active">
            <h3 style="color: #667eea; margin-bottom: 15px;">最近30天每日报告</h3>
            <div id="reportsList">
                {self._generate_reports_html(recent_reports)}
            </div>
        </div>

        <!-- 训练日志标签页 -->
        <div id="training" class="tab-content">
            <h3 style="color: #667eea; margin-bottom: 15px;">最近30条训练日志</h3>
            <div id="trainingList">
                {self._generate_training_html(recent_logs)}
            </div>
        </div>

        <!-- 数据分析标签页 -->
        <div id="charts" class="tab-content">
            <h3 style="color: #667eea; margin-bottom: 15px;">训练数据分析（30天）</h3>
            <div class="chart-container">
                <canvas id="trainingChart"></canvas>
            </div>
        </div>

        <!-- 添加记录标签页 -->
        <div id="add" class="tab-content">
            <div id="healthForm" class="add-form">
                <h3 style="color: #667eea; margin-bottom: 15px;">➕ 添加健康记录</h3>
                <form onsubmit="addHealthRecord(event)">
                    <div class="form-group">
                        <label>日期（YYYY-MM-DD）：</label>
                        <input type="date" id="healthDate" required>
                    </div>
                    <div class="form-group">
                        <label>准备度分数（0-100）：</label>
                        <input type="number" id="healthReadiness" min="0" max="100" required>
                    </div>
                    <div class="form-group">
                        <label>训练内容：</label>
                        <textarea id="healthContent" placeholder="记录今天的训练内容..."></textarea>
                    </div>
                    <button type="submit" class="submit-btn">💾 保存记录</button>
                </form>
            </div>

            <div id="trainingForm" class="add-form">
                <h3 style="color: #667eea; margin-bottom: 15px;">➕ 添加训练记录</h3>
                <form onsubmit="addTrainingRecord(event)">
                    <div class="form-group">
                        <label>日期（YYYY-MM-DD）：</label>
                        <input type="date" id="trainingDate" required>
                    </div>
                    <div class="form-group">
                        <label>训练类型：</label>
                        <select id="trainingType" required>
                            <option value="">请选择...</option>
                            <option value="泳池训练（四项基础）">泳池训练（四项基础）</option>
                            <option value="1000米蛙泳">1000米蛙泳</option>
                            <option value="陆地训练">陆地训练</option>
                            <option value="恢复训练">恢复训练</option>
                            <option value="其他">其他</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>地点：</label>
                        <input type="text" id="trainingLocation" placeholder="如：静安体育中心" required>
                    </div>
                    <div class="form-group">
                        <label>时长（分钟）：</label>
                        <input type="number" id="trainingDuration" min="0" required>
                    </div>
                    <div class="form-group">
                        <label>训练内容：</label>
                        <textarea id="trainingContent" placeholder="详细记录训练内容..." rows="5"></textarea>
                    </div>
                    <div class="form-group">
                        <label>训练数据：</label>
                        <textarea id="trainingData" placeholder="如：总时间=17分56秒，配速=1:47/100m" rows="3"></textarea>
                    </div>
                    <button type="submit" class="submit-btn">💾 保存记录</button>
                </form>
            </div>
        </div>

        <div class="update-info">
            最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            下次更新：{(datetime.now() + timedelta(hours=3)).strftime('%H:%M')}（每3小时自动刷新）
        </div>
    </div>

    <script>
        // 记录数据
        const recordsData = {json.dumps({
            "daily_reports": dict(list(self.records["daily_reports"].items())[:30]),
            "training_logs": dict(list(self.records["training_logs"].items())[:30])
        })};

        // 切换标签页
        function switchTab(tabName) {{
            // 隐藏所有标签页内容
            document.querySelectorAll('.tab-content').forEach(el => {{
                el.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(el => {{
                el.classList.remove('active');
            }});

            // 显示选中的标签页
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');

            // 如果是添加记录，显示对应的表单
            if (tabName === 'add') {{
                document.getElementById('healthForm').classList.add('active');
                document.getElementById('trainingForm').classList.remove('active');
            }}

            // 如果是数据分析，生成图表
            if (tabName === 'charts') {{
                generateCharts();
            }}
        }}

        // 打开添加表单
        function openAddForm(type) {{
            switchTab('add');
            if (type === 'health') {{
                document.getElementById('healthForm').classList.add('active');
                document.getElementById('trainingForm').classList.remove('active');
            }} else {{
                document.getElementById('trainingForm').classList.add('active');
                document.getElementById('healthForm').classList.remove('active');
            }}
        }}

        // 搜索记录
        function searchRecords() {{
            const keyword = document.getElementById('searchInput').value.toLowerCase();
            const resultsDiv = document.getElementById('searchResults');

            if (!keyword) {{
                resultsDiv.innerHTML = '<p style="color: #666;">请输入关键词</p>';
                return;
            }}

            let results = [];

            // 搜索每日报告
            for (const [date, report] of Object.entries(recordsData.daily_reports)) {{
                const content = report.content.toLowerCase();
                if (content.includes(keyword)) {{
                    results.push({{
                        type: '每日报告',
                        date: date,
                        summary: content.substring(0, 200) + '...'
                    }});
                }}
            }}

            // 搜索训练日志
            for (const [date, log] of Object.entries(recordsData.training_logs)) {{
                const content = JSON.stringify(log).toLowerCase();
                if (content.includes(keyword)) {{
                    results.push({{
                        type: '训练日志',
                        date: date,
                        summary: log.content ? log.content.substring(0, 200) : log.training_type
                    }});
                }}
            }}

            if (results.length === 0) {{
                resultsDiv.innerHTML = '<p style="color: #666;">未找到匹配记录</p>';
            }} else {{
                resultsDiv.innerHTML = '<h4 style="color: #667eea; margin-bottom: 10px;">搜索结果（' + results.length + '条）</h4>';
                results.forEach(result => {{
                    resultsDiv.innerHTML += `
                        <div class="result-item" onclick="viewRecord('${{result.type}}', '${{result.date}}')">
                            <strong>${{result.date}}</strong> - ${{{result.type}}}<br>
                            <small>${{result.summary}}</small>
                        </div>
                    `;
                }});
            }}
        }}

        // 查看记录详情
        function viewRecord(type, date) {{
            if (type === '每日报告') {{
                const report = recordsData.daily_reports[date];
                if (report) {{
                    window.open('file://' + report.file, '_blank');
                }}
            }} else if (type === '训练日志') {{
                const log = recordsData.training_logs[date];
                if (log) {{
                    alert(`日期：${{log.date}}\\n类型：${{log.training_type}}\\n地点：${{log.location}}\\n\\n${{log.content}}`);
                }}
            }}
        }}

        // 展开详情
        function toggleDetail(id) {{
            const detail = document.getElementById('detail-' + id);
            const btn = document.getElementById('btn-' + id);
            if (detail.classList.contains('expanded')) {{
                detail.classList.remove('expanded');
                btn.textContent = '查看详情 ▼';
            }} else {{
                detail.classList.add('expanded');
                btn.textContent = '收起 ▲';
            }}
        }}

        // 添加健康记录
        function addHealthRecord(event) {{
            event.preventDefault();
            alert('健康记录已添加！（演示功能，实际使用需要后端支持）');
        }}

        // 添加训练记录
        function addTrainingRecord(event) {{
            event.preventDefault();
            alert('训练记录已添加！（演示功能，实际使用需要后端支持）');
        }}

        // 生成数据分析图表
        function generateCharts() {{
            // 这里可以生成训练数据分析图表
            const ctx = document.getElementById('trainingChart');

            // 模拟数据
            const dates = ['1/1', '1/2', '1/3', '1/4', '1/5', '1/6', '1/7'];
            const trainingCount = [3, 4, 2, 5, 4, 3, 4];

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: dates,
                    datasets: [{{
                        label: '训练次数',
                        data: trainingCount,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{ stepSize: 1 }}
                        }}
                    }}
                }}
            }});
        }}

        // 自动刷新（每3小时）
        setTimeout(function() {{
            location.reload();
        }}, 3 * 60 * 60 * 1000);

        // 搜索框回车搜索
        document.getElementById('searchInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                searchRecords();
            }}
        }});
    </script>
</body>
</html>"""

        return html

def generate_reports_html(self, reports):
        """生成报告HTML"""
        html = ""
        for date, report in reports[:10]:  # 只显示前10个
            content_preview = report["content"][:300].replace("\n", " ")
            html += f"""
            <div class="record-card">
                <div class="record-date">📅 {report['date']}</div>
                <div class="record-summary">{content_preview}...</div>
                <div class="record-detail" id="detail-{date}">
                    <pre style="white-space: pre-wrap; font-size: 14px;">{report['content'][:1500]}</pre>
                </div>
                <button class="expand-btn" id="btn-{date}" onclick="toggleDetail('{date}')">查看详情 ▼</button>
            </div>
            """
        return html

    def generate_training_html(self, logs):
        """生成训练日志HTML"""
        html = ""
        for date, log in logs[:10]:  # 只显示前10个
            content = log.get("content", log.get("summary", "无详细内容"))
            html += f"""
            <div class="record-card">
                <div class="record-date">🏋️ {date}</div>
                <div class="record-summary">
                    <strong>类型：</strong>{log.get('training_type', '未分类')}<br>
                    <strong>地点：</strong>{log.get('location', '未知地点')}<br>
                    <strong>时长：</strong>{log.get('duration', 0)}分钟
                </div>
                <div class="record-detail" id="detail-training-{date}">
                    <pre style="white-space: pre-wrap; font-size: 14px;">{content[:1000]}</pre>
                </div>
                <button class="expand-btn" id="btn-training-{date}" onclick="toggleDetail('training-{date}')">查看详情 ▼</button>
            </div>
            """
        return html

    def start_auto_update_server(self, port=8000):
        """启动自动更新服务器"""

        class RecordsHTTPRequestHandler(SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                super().end_headers()

        def log_message(self, format, *args):
            pass  # 禁用日志输出

        server = HTTPServer(('localhost', port), RecordsHTTPRequestHandler, log_level=0)

        print(f"🌐 记录管理系统服务器已启动：http://localhost:{port}")
        print(f"📂 服务目录：{self.base_dir}")
        print(f"⏰ 每3小时自动刷新一次")
        print(f"按 Ctrl+C 停止服务器")

        # 在浏览器中打开
        import webbrowser
        webbrowser.open(f'http://localhost:{port}')

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ 服务器已停止")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="金明完整记录管理系统")
    parser.add_argument("--scan", action="store_true", help="扫描所有报告文件")
    parser.add_argument("--viewer", action="store_true", help="打开记录查看器")
    parser.add_argument("--server", action="store_true", help="启动Web服务器（每3小时自动更新）")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口（默认8000）")

    args = parser.parse_args()

    system = RecordManagementSystem()

    if args.scan:
        system.scan_all_reports()
        print("\n✓ 扫描完成，数据库已更新")

    if args.viewer:
        html = system.generate_records_viewer_html()
        viewer_file = Path("records_viewer.html")
        with open(viewer_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n✓ 记录查看器已生成：{viewer_file}")
        import webbrowser
        webbrowser.open(f'file://{viewer_file.absolute()}')

    if args.server:
        if not system.records["daily_reports"]:
            print("⚠️ 正在扫描报告...")
            system.scan_all_reports()

        print("\n🚀 启动自动更新服务器...")
        system.start_auto_update_server(args.port)


if __name__ == "__main__":
    main()
"""

# 创建记录管理系统实例
system = RecordManagementSystem()

# 扫描所有报告
system.scan_all_reports()

# 生成HTML查看器
html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金明 - 完整记录管理系统</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
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
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }}
        .stat {{
            text-target: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .quick-links {{
            background: white;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            text-align: center;
        }}
        .quick-links a {{
            display: inline-block;
            margin: 5px 10px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 14px;
        }}
        .dashboard-links {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        .dashboard-links h3 {{
            color: #667eea;
            margin-bottom: 15px;
            text-align: center;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
        }}
        .dashboard-link {{
            display: block;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
        }}
        .records-section {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        .record-item {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background: #f9f9f9;
        }}
        .record-date {{
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .update-info {{
            text-align: center;
            color: white;
            padding: 15px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏊 金明 - 完整记录管理系统</h1>
            <p>查看每日健康报告 + 训练日志 | 每3小时自动更新</p>

            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(system.records['daily_reports'])}</div>
                    <div class="stat-label">每日报告</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(system.records['training_logs'])}</div>
                    <div class="stat-label">训练日志</div>
                </div>
                <div class="stat">
                    <div class="stat-value">30</div>
                    <div class="stat-label">最近天数</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{datetime.now().strftime('%H:%M')}</div>
                    <div class="stat-label">更新时间</div>
                </div>
            </div>
        </div>

        <!-- 快速链接 -->
        <div class="quick-links">
            <a href="super_dashboard.html" target="_blank">📊 打开今日看板</a>
            <a href="dashboard_with_charts.html" target="_blank">📈 专业可视化看板</a>
            <a href="#" onclick="location.reload()">🔄 立即刷新</a>
        </div>

        <!-- 看板链接 -->
        <div class="dashboard-links">
            <h3>📊 所有看板</h3>
            <div class="dashboard-grid">
                <a href="super_dashboard.html" target="_blank" class="dashboard-link">
                    超级增强看板<br><small>8个图表</small>
                </a>
                <a href="dashboard_with_charts.html" target="_blank" class="dashboard-link">
                    专业可视化看板<br><small>6个交互图表</small>
                </a>
                <a href="dashboard_2026-02-04.html" target="_blank" class="dashboard-link">
                    基础HTML看板<br><small>完整内容</small>
                </a>
                <a href="dashboard_2026-02-04.md" target="_blank" class="dashboard-link">
                    Markdown看板<br><small>1010行</small>
                </a>
            </div>
        </div>

        <!-- 最近记录 -->
        <div class="records-section">
            <h3 style="color: #667eea;">📋 最近30天每日报告</h3>
"""

        # 添加最近的每日报告
        recent_reports = sorted(
            system.records["daily_reports"].items(),
            key=lambda x: x[0],
            reverse=True
        )[:10]

        for date, report in recent_reports:
            content_preview = report["content"][:200].replace("\n", " ")
            html_content += f"""
            <div class="record-item">
                <div class="record-date">📅 {date}</div>
                <p style="color: #333; line-height: 1.6;">{content_preview}...</p>
                <p>
                    <a href="dashboard_{date}.html" target="_blank" style="color: #667eea; text-decoration: underline;">查看完整报告 →</a>
                </p>
            </div>
            """

        html_content += """
        </div>

        <div class="update-info">
            <strong>最后更新：</strong>""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """<br>
            <strong>下次更新：</strong>""" + (datetime.now() + timedelta(hours=3)).strftime('%H:%M') + """（每3小时自动刷新）<br>
            <strong>数据来源：</strong>DailyReports + TrainingLogs
        </div>
    </div>

    <script>
        // 自动刷新（每3小时）
        setTimeout(function() {{
            location.reload();
        }}, 3 * 60 * 60 * 1000);
    </script>
</body>
</html>
"""

# 保存记录查看器
viewer_file = Path.cwd() / "records_viewer.html"
with open(viewer_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ 记录管理系统已创建！")
print(f"\n📂 文件：{viewer_file.absolute()}")
print(f"🌐 在浏览器中打开，包含：")
print(f"  ✓ {len(system.records['daily_reports'])} 天每日报告")
print(f"  ✓ {len(system.records['training_logs'])} 条训练日志")
print(f"  ✓ 所有看板链接")
print(f"  ✓ 每3小时自动刷新")

# 在浏览器中打开
import webbrowser
webbrowser.open(f'file://{viewer_file.absolute()}')

print(f"\n✅ 记录管理系统已在浏览器中打开！")
print(f"📊 包含：每日报告 + 训练日志 + 所有看板链接")
