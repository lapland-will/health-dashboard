# 训练日志系统 - 完整使用指南

**更新时间：** 2026-02-04
**状态：** ✅ 已完成并可用

---

## 📋 系统功能

### 1. 训练日志输入与管理
- ✅ 直接输入和提交训练日志
- ✅ 自动按天、月排序
- ✅ 搜索功能
- ✅ 统计分析

### 2. 肺活量数据管理
- ✅ 已导入50条历史记录
- ✅ PB: 8000ml (2024.6.24)
- ✅ 支持新增测量记录
- ✅ 自动更新PB

### 3. 个人最好成绩（PB）
- ✅ DNF: 212米
- ✅ DYN: 319米
- ✅ DYNB: 287米
- ✅ STA: 9分08秒 (548秒)
- ✅ 肺活量: 7962ml (用户指定)

---

## 🚀 快速开始

### 方式1：使用启动脚本（推荐）

```bash
# 进入目录
cd /Users/williamjoy/Desktop/AI/QuantTrading/QuantTrading/Personal/Health

# 运行启动脚本
bash start_log_system.sh
```

### 方式2：直接运行Python

```bash
cd /Users/williamjoy/Desktop/AI/QuantTrading/QuantTrading/Personal/Health
python3 log_server.py
```

### 方式3：双击启动（Mac）

在Finder中找到 `start_log_system.sh`，双击运行

---

## 🌐 访问系统

启动后，在浏览器访问：

**主界面：** http://localhost:5000

**API端点：**
- GET/POST http://localhost:5000/api/training-log - 训练日志
- GET/POST http://localhost:5000/api/lung-capacity - 肺活量
- GET/POST http://localhost:5000/api/personal-best - PB
- GET http://localhost:5000/api/statistics - 统计数据

---

## 📝 使用说明

### 1. 添加训练日志

**步骤：**

1. 访问 http://localhost:5000
2. 点击"🏋️ 训练日志"标签
3. 填写表单：
   - 日期：自动填充为今天
   - 训练类型：泳池训练/陆地训练/休息日/比赛
   - 训练内容：详细描述
   - 指标（可选）：
     - 距离（米）
     - 时间（秒）
     - 尝试次数
   - 备注：身体感觉、疲劳度等
4. 点击"提交训练日志"

**示例：**
```
日期: 2026-02-04
训练类型: 泳池训练
训练内容: 热身15分钟，四项基础训练（无蹼8×25米，单蹼6×25米，
双蹼8×25米，静态闭气4组），1000米蛙泳测试
距离: 1000
时间: 1146
尝试次数: 10
备注: 感觉良好，准备度86分
```

### 2. 添加肺活量测量

**步骤：**

1. 点击"🫁 肺活量测量"标签
2. 填写表单：
   - 日期：自动填充为今天
   - 测量值：可输入1-3个测量值（ml）
   - 备注：测量条件、感受等
3. 点击"提交肺活量数据"

**示例：**
```
日期: 2026-02-04
测量值: [7800, 7900, 7962]
备注: 早晨空腹测量，使用长笛型肺活量计
```

**统计数据：**
- 总记录数：50条
- PB: 8000ml (2024.6.24)
- 平均值：自动计算
- 最近记录：显示最近10条

### 3. 更新个人最好成绩（PB）

**步骤：**

1. 点击"🏆 个人最好成绩"标签
2. 查看当前PB：
   - DNF: 212米
   - DYN: 319米
   - DYNB: 287米
   - STA: 9:08
3. 如需更新：
   - 选择项目
   - 输入新成绩
   - 输入日期（可选）
   - 输入地点（可选）
   - 点击"更新PB"

**示例：**
```
项目: STA
成绩: 9:15
日期: 2026-02-04
地点: 上海游泳馆
```

### 4. 查看与分析数据

**步骤：**

1. 点击"📊 数据查看"标签
2. 选择查看类型：
   - 训练日志
   - 肺活量记录
   - PB历史
3. 选择时间范围：
   - 最近7天
   - 最近30天
   - 最近90天
   - 最近一年
   - 全部

---

## 📂 数据存储位置

所有数据保存在：

```
Personal/Health/TrainingLogs/
├── training_logs.json      # 训练日志
├── lung_capacity.json      # 肺活量数据
├── personal_best.json      # 个人最好成绩
└── backup_*.json           # 自动备份
```

---

## 🔧 技术说明

### 数据格式

#### training_logs.json
```json
{
  "logs": [
    {
      "date": "2026-02-04",
      "training_type": "泳池训练",
      "content": "训练内容描述",
      "metrics": {
        "distance": 1000,
        "time": 1146,
        "attempts": 10
      },
      "notes": "备注",
      "created_at": "2026-02-04T15:30:00"
    }
  ],
  "metadata": {
    "created": "2026-02-04T00:00:00",
    "last_updated": "2026-02-04T15:30:00"
  }
}
```

#### lung_capacity.json
```json
{
  "pb": 8000,
  "pb_date": "2024.6.24",
  "records": [
    {
      "date": "2024.6.24",
      "measurements": [7800, 7900, 8000],
      "max_today": 8000,
      "notes": "早晨空腹测量",
      "created_at": "2026-02-04T15:30:00"
    }
  ]
}
```

#### personal_best.json
```json
{
  "DNF": {"distance": 212, "date": null, "location": null},
  "DYN": {"distance": 319, "date": null, "location": null},
  "DYNB": {"distance": 287, "date": null, "location": null},
  "STA": {"time": "9:08", "seconds": 548, "date": null, "location": null},
  "lung_capacity": {"pb": 7962, "pb_date": null}
}
```

---

## 🔌 API文档

### POST /api/training-log

添加训练日志

**请求体：**
```json
{
  "date": "2026-02-04",
  "training_type": "泳池训练",
  "content": "训练内容",
  "metrics": {
    "distance": 1000,
    "time": 1146,
    "attempts": 10
  },
  "notes": "备注"
}
```

**响应：**
```json
{
  "success": true,
  "log": {...}
}
```

### GET /api/training-log?days=30

获取训练日志

**参数：**
- days: 最近多少天（默认30）
- month: 月份（01-12）
- year: 年份（如2026）

**响应：**
```json
{
  "logs": [...]
}
```

### POST /api/lung-capacity

添加肺活量记录

**请求体：**
```json
{
  "date": "2026-02-04",
  "measurements": [7800, 7900, 8000],
  "notes": "备注"
}
```

**响应：**
```json
{
  "success": true,
  "record": {...},
  "pb": 8000
}
```

### GET /api/lung-capacity

获取肺活量数据

**响应：**
```json
{
  "pb": 8000,
  "pb_date": "2024.6.24",
  "records": [...]
}
```

### POST /api/personal-best

更新PB

**请求体：**
```json
{
  "event": "STA",
  "value": "9:15",
  "date": "2026-02-04",
  "location": "上海"
}
```

**响应：**
```json
{
  "success": true,
  "pb": {...},
  "all": {...}
}
```

### GET /api/statistics?days=30

获取统计数据

**参数：**
- days: 统计周期（默认30）

**响应：**
```json
{
  "period_days": 30,
  "training_logs": {
    "total": 15,
    "by_type": {
      "泳池训练": 10,
      "陆地训练": 3,
      "休息日": 2
    }
  },
  "lung_capacity": {
    "records": 5,
    "avg": 7850,
    "max": 8000,
    "trend": [7800, 7900, 8000, 7850, 7900]
  }
}
```

---

## 🔄 自动更新到图表

每次提交数据后：

1. ✅ 数据自动保存到JSON文件
2. ✅ 统计数据实时更新
3. ⚠️ 图表更新：需要重新运行 `ultimate_dashboard.py`

**更新图表：**
```bash
cd /Users/williamjoy/Desktop/AI/QuantTrading/QuantTrading/Personal/Health
python3 ultimate_dashboard.py
```

---

## 📱 从首页访问

在主首页（index.html）已添加"训练日志输入系统"链接：

1. 打开 `index.html`
2. 滚动到"其他看板版本"部分
3. 点击"📝 训练日志输入系统"
4. 按照提示启动服务器
5. 访问 http://localhost:5000

---

## ⚠️ 注意事项

### 数据备份

- 数据保存在本地JSON文件
- 建议定期备份 `TrainingLogs/` 文件夹
- 可使用API导出完整数据

### 服务器运行

- 服务器占用端口5000
- 只在运行时可访问
- Ctrl+C停止服务器
- 可以后台运行：
  ```bash
  nohup python3 log_server.py > server.log 2>&1 &
  ```

### 数据安全

- 所有数据存储在本地
- 不会上传到云端
- 建议定期备份

---

## 🛠️ 故障排除

### 问题1：服务器启动失败

**错误：** `Address already in use`

**解决：**
```bash
# 查找占用端口的进程
lsof -i :5000

# 结束进程
kill -9 <PID>

# 或使用其他端口
python3 log_server.py  # 修改代码中的端口号
```

### 问题2：数据未保存

**检查：**
1. `TrainingLogs/` 文件夹是否存在
2. 是否有写入权限
3. 查看服务器日志

### 问题3：无法访问界面

**检查：**
1. 服务器是否正在运行
2. 浏览器地址是否正确
3. 防火墙是否阻止

---

## 📊 已导入数据

### 肺活量历史记录

- ✅ 总记录：50条
- ✅ 时间范围：2023.11 - 2024.10
- ✅ PB: 8000ml (2024.6.24)
- ✅ 数据来源：金明自由潜/肺活量测量表.xlsx

**最近5条记录：**
- 2024.9.23: 7363 ml
- 2024.9.27: 7453 ml
- 2024.10.3: 7907 ml
- 2024.10.6: 7804 ml
- 2024.10.9: 7658 ml

---

## 🎯 下一步

### 立即开始：

1. **启动服务器**
   ```bash
   cd /Users/williamjoy/Desktop/AI/QuantTrading/QuantTrading/Personal/Health
   bash start_log_system.sh
   ```

2. **访问界面**
   - 浏览器打开: http://localhost:5000

3. **输入第一条日志**
   - 选择训练日志标签
   - 填写今日训练内容
   - 提交

4. **验证数据**
   - 查看数据标签
   - 确认记录已保存
   - 检查统计数据

### 未来扩展：

- [ ] 添加图表可视化
- [ ] 导出为Excel/PDF
- [ ] 自动生成训练报告
- [ ] 与Oura Ring数据整合
- [ ] 设置训练目标提醒

---

**状态：✅ 系统已完成并可用**

*最后更新：2026-02-04*
