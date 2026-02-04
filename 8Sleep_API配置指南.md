# 8Sleep API 配置指南

## 📖 如何获取8Sleep API Key

### 步骤1：登录8Sleep账户
访问：https://app.8slp.net/

### 步骤2：获取API密钥
1. 登录后，进入设置（Settings）
2. 找到"API Access"或"开发者选项"
3. 生成API密钥

### 步骤3：配置到系统

在 `ultimate_dashboard.py` 文件中，找到以下行：

```python
# 8Sleep API配置（需要用户提供）
self.eightsleep_api_key = None  # 需要配置
self.eightsleep_user_id = None  # 需要配置
```

将 `None` 替换为您的实际API密钥：

```python
self.eightsleep_api_key = "YOUR_API_KEY_HERE"
self.eightsleep_user_id = "YOUR_USER_ID_HERE"  # 可选
```

---

## 📊 8Sleep API 数据说明

### API端点
- **基础URL：** `https://api.8slp.net/v1`
- **睡眠会话：** `/users/me/sessions`

### 返回的数据字段
- `score.total` - 睡眠总分 (0-100)
- `duration.total` - 总睡眠时长（秒）
- `duration.light` - 浅睡时长（秒）
- `duration.deep` - 深睡时长（秒）
- `duration.rem` - REM时长（秒）
- `timeToSleep` - 入睡时间（分钟）
- `tossAndTurn.total` - 翻身次数
- `respiration.avg` - 平均呼吸率
- `heartRate.avg` - 平均心率
- `heartRate.min` - 最低心率
- `temp.min/avg` - 床垫温度
- `tempRoom.min/avg` - 房间温度

### 数据权限
需要确保您的8Sleep账户有API访问权限。

---

## 🔧 测试API连接

配置API密钥后，运行以下命令测试：

```bash
cd ~/Desktop/AI/QuantTrading/QuantTrading/Personal/Health
python3 ultimate_dashboard.py
```

如果配置正确，您会看到：
```
✓ 8Sleep数据获取完成: 睡眠分数 XX/100
```

如果未配置，会看到：
```
⚠️ 8Sleep API未配置，跳过
```

---

## 📋 8Sleep数据将显示在看板的

### 🛏️ 8Sleep智能床垫数据 部分

包含以下信息：
- 睡眠总分
- 总睡眠时长、浅睡、深睡、REM时长
- 入睡时间、翻身次数
- 平均呼吸率、心率数据
- 床垫温度、房间温度
- 睡眠质量分析（深睡占比、REM占比、睡眠安稳度）

---

## ⚠️ 当前状态

**8Sleep API未配置** - 系统会跳过8Sleep数据获取，不影响其他功能。

如果您有8Sleep设备，请按照上述步骤配置API密钥，系统将自动整合8Sleep数据到看板中。

---

## 📞 需要帮助？

如果配置过程中遇到问题：
1. 确认API密钥格式正确
2. 检查网络连接
3. 查看8Sleep官方文档：https://8sleep.gitbook.io/getting-started/

---

**配置完成后，每天上午11点的自动报告将包含8Sleep数据！**
