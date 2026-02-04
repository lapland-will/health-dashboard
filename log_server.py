#!/usr/bin/env python3
"""
训练日志系统 - Flask API服务器
处理训练日志、肺活量、PB数据的存储和分析
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from pathlib import Path
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# 数据路径
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "TrainingLogs"
TRAINING_LOGS_FILE = LOGS_DIR / "training_logs.json"
LUNG_CAPACITY_FILE = LOGS_DIR / "lung_capacity.json"
PERSONAL_BEST_FILE = LOGS_DIR / "personal_best.json"

# 确保目录存在
LOGS_DIR.mkdir(exist_ok=True)


def load_json_file(file_path, default_data):
    """加载JSON文件"""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default_data


def save_json_file(file_path, data):
    """保存JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 初始化数据
def init_data():
    """初始化数据文件"""
    # 训练日志
    if not TRAINING_LOGS_FILE.exists():
        save_json_file(TRAINING_LOGS_FILE, {
            "logs": [],
            "metadata": {"created": datetime.now().isoformat()}
        })

    # 肺活量数据（如果不存在，从已有文件复制）
    if not LUNG_CAPACITY_FILE.exists():
        existing_lung = LOGS_DIR / "lung_capacity.json"
        if existing_lung.exists():
            # 文件已存在，不需要操作
            pass
        else:
            save_json_file(LUNG_CAPACITY_FILE, {
                "pb": 7962,
                "pb_date": None,
                "records": []
            })

    # PB数据
    if not PERSONAL_BEST_FILE.exists():
        save_json_file(PERSONAL_BEST_FILE, {
            "DNF": {"distance": 212, "date": None, "location": None},
            "DYN": {"distance": 319, "date": None, "location": None},
            "DYNB": {"distance": 287, "date": None, "location": None},
            "STA": {"time": "9:08", "seconds": 548, "date": None, "location": None}
        })


init_data()


@app.route('/')
def index():
    """主页"""
    return send_from_directory(BASE_DIR, 'log_input.html')


@app.route('/api/training-log', methods=['GET', 'POST'])
def training_log():
    """训练日志API"""
    if request.method == 'POST':
        # 添加新日志
        data = request.json

        log = {
            "date": data.get('date'),
            "training_type": data.get('training_type'),
            "content": data.get('content'),
            "metrics": data.get('metrics', {}),
            "notes": data.get('notes', ''),
            "created_at": datetime.now().isoformat()
        }

        # 加载现有数据
        logs_data = load_json_file(TRAINING_LOGS_FILE, {"logs": []})
        logs_data["logs"].append(log)
        logs_data["metadata"]["last_updated"] = datetime.now().isoformat()

        # 保存
        save_json_file(TRAINING_LOGS_FILE, logs_data)

        return jsonify({"success": True, "log": log})

    else:
        # GET请求 - 获取日志
        days = request.args.get('days', 30, type=int)
        month = request.args.get('month')
        year = request.args.get('year')

        logs_data = load_json_file(TRAINING_LOGS_FILE, {"logs": []})
        logs = logs_data.get("logs", [])

        # 按日期过滤
        if month and year:
            logs = [log for log in logs if log["date"].startswith(f"{year}-{month.zfill(2)}")]
        elif days:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            logs = [log for log in logs if log["date"] >= cutoff]

        # 按日期排序
        logs = sorted(logs, key=lambda x: x["date"], reverse=True)

        return jsonify({"logs": logs})


@app.route('/api/lung-capacity', methods=['GET', 'POST'])
def lung_capacity():
    """肺活量API"""
    if request.method == 'POST':
        # 添加新记录
        data = request.json

        measurements = [m for m in data.get('measurements', []) if m > 0]
        if not measurements:
            return jsonify({"success": False, "error": "No valid measurements"}), 400

        max_today = max(measurements)

        record = {
            "date": data.get('date'),
            "measurements": measurements,
            "max_today": max_today,
            "notes": data.get('notes', ''),
            "created_at": datetime.now().isoformat()
        }

        # 加载现有数据
        lung_data = load_json_file(LUNG_CAPACITY_FILE, {"pb": 7962, "records": []})
        lung_data["records"].append(record)

        # 更新PB
        if max_today > lung_data.get("pb", 0):
            lung_data["pb"] = max_today
            lung_data["pb_date"] = data.get('date')

        # 保存
        save_json_file(LUNG_CAPACITY_FILE, lung_data)

        return jsonify({"success": True, "record": record, "pb": lung_data["pb"]})

    else:
        # GET请求 - 获取数据
        lung_data = load_json_file(LUNG_CAPACITY_FILE, {"pb": 7962, "records": []})

        # 按日期排序
        lung_data["records"] = sorted(lung_data["records"], key=lambda x: x["date"])

        return jsonify(lung_data)


@app.route('/api/personal-best', methods=['GET', 'POST'])
def personal_best():
    """个人最好成绩API"""
    if request.method == 'POST':
        # 更新PB
        data = request.json
        event = data.get('event')

        if event not in ['DNF', 'DYN', 'DYNB', 'STA']:
            return jsonify({"success": False, "error": "Invalid event"}), 400

        # 加载现有数据
        pb_data = load_json_file(PERSONAL_BEST_FILE, {})

        if event == 'STA':
            # 静态闭气 - 时间格式
            value = data.get('value')
            if isinstance(value, str) and ':' in value:
                parts = value.split(':')
                seconds = int(parts[0]) * 60 + int(parts[1])
            else:
                seconds = int(value)
                value = f"{seconds // 60}:{seconds % 60:02d}"

            pb_data[event] = {
                "time": value,
                "seconds": seconds,
                "date": data.get('date'),
                "location": data.get('location')
            }
        else:
            # 距离项目
            pb_data[event] = {
                "distance": int(data.get('value')),
                "date": data.get('date'),
                "location": data.get('location')
            }

        # 保存
        save_json_file(PERSONAL_BEST_FILE, pb_data)

        return jsonify({"success": True, "pb": pb_data[event], "all": pb_data})

    else:
        # GET请求 - 获取PB
        pb_data = load_json_file(PERSONAL_BEST_FILE, {})
        return jsonify(pb_data)


@app.route('/api/statistics')
def statistics():
    """统计数据API"""
    days = request.args.get('days', 30, type=int)

    # 训练日志统计
    logs_data = load_json_file(TRAINING_LOGS_FILE, {"logs": []})
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    recent_logs = [log for log in logs_data.get("logs", []) if log["date"] >= cutoff]

    training_types = {}
    for log in recent_logs:
        ttype = log.get("training_type", "未知")
        training_types[ttype] = training_types.get(ttype, 0) + 1

    # 肺活量统计
    lung_data = load_json_file(LUNG_CAPACITY_FILE, {"records": []})
    lung_records = [r for r in lung_data.get("records", []) if r["date"] >= cutoff]
    lung_values = [r["max_today"] for r in lung_records]

    stats = {
        "period_days": days,
        "training_logs": {
            "total": len(recent_logs),
            "by_type": training_types
        },
        "lung_capacity": {
            "records": len(lung_records),
            "avg": sum(lung_values) / len(lung_values) if lung_values else 0,
            "max": max(lung_values) if lung_values else 0,
            "trend": lung_values[-7:] if len(lung_values) >= 7 else lung_values
        }
    }

    return jsonify(stats)


if __name__ == '__main__':
    print("🚀 训练日志系统服务器启动中...")
    print("📝 访问: http://localhost:5000")
    print("📊 API文档: http://localhost:5000/api/statistics")
    app.run(debug=True, port=5000, host='0.0.0.0')
