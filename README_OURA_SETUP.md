# Oura Ring 数据对接设置指南

**用户：** 金明 (William Joy) - 自由潜水世界纪录保持者
**设置日期：** 2025-01-31

---

## 📋 已创建的文件

### 1. 数据同步脚本
- **文件：** `oura_ring_sync.py`
- **功能：** 从Oura Ring API获取健康数据并保存到本地

### 2. 数据分析脚本
- **文件：** `oura_ring_analyzer.py`
- **功能：** 分析Oura数据并生成报告，特别针对自由潜水运动员优化

### 3. 数据目录
- **目录：** `OuraData/`
- **内容：** 存储所有导出的JSON和CSV数据文件
- **报告：** `OuraData/Reports/` - 存储分析报告

---

## 🔑 获取Personal Access Token

### 步骤：

1. **访问Oura Cloud**
   - 打开浏览器访问: https://cloud.ouraring.com/personal-access-tokens

2. **创建Access Token**
   - 点击 "Create Personal Access Token"
   - 输入一个描述性名称（如："Claude Sync"）
   - 选择权限范围（建议全部选中）
   - 点击 "Create"

3. **复制Token**
   - ⚠️ Token只显示一次，请立即复制保存
   - Token格式类似：`OURA_XXXXXXXXXXXX`

---

## ⚙️ 设置方法

### 方法一：环境变量（推荐）

```bash
# 在终端中运行
export OURA_ACCESS_TOKEN='your_token_here'

# 然后运行同步脚本
cd ~/Desktop/AI/QuantTrading/QuantTrading/Personal/Health
python3 oura_ring_sync.py
```

### 方法二：直接运行脚本

```bash
cd ~/Desktop/AI/QuantTrading/QuantTrading/Personal/Health
python3 oura_ring_sync.py
# 脚本会提示输入token
```

---

## 📊 使用方法

### 1. 同步数据

```bash
# 同步最近30天的数据
python3 oura_ring_sync.py

# 或在Python中
from oura_ring_sync import OuraRingDataSync

sync = OuraRingDataSync('your_token')
sync.sync_all(days=30)  # 获取最近30天
```

### 2. 分析数据

```bash
# 生成分析报告
python3 oura_ring_analyzer.py
```

### 3. 定期自动同步（推荐）

使用cron或launchd设置每日自动同步：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天早上8点同步）
0 8 * * * cd ~/Desktop/AI/QuantTrading/QuantTrading/Personal/Health && /usr/bin/python3 oura_ring_sync.py >> oura_sync.log 2>&1
```

---

## 📈 数据类型

脚本会同步以下数据：

1. **每日睡眠数据** (`daily_sleep`)
   - 睡眠分数、深度睡眠、REM睡眠
   - 睡眠效率、总时长
   - 就寝和起床时间

2. **每日活动数据** (`daily_activity`)
   - 活动分数、步数、卡路里
   - 活动类型分布

3. **每日准备度** (`daily_readiness`)
   - 整体准备度分数
   - 恢复指数
   - HRV平衡
   - 睡眠对准备度的影响

4. **心率数据** (`heartrate`)
   - 时间序列心率数据
   - 适合详细分析

5. **睡眠时间序列** (`sleep_timeseries`)
   - 详细的睡眠阶段数据
   - 睡眠期间的心率和HRV

---

## 🎯 对自由潜水训练的特别关注

分析脚本会特别关注以下指标：

### 1. **心率变异性 (HRV)**
- 反映自主神经系统平衡
- 高HRV = 良好的恢复状态
- 低HRV = 可能疲劳或过度训练

### 2. **恢复指数**
- 综合评估身体恢复状态
- 指导当日训练强度

### 3. **睡眠质量**
- 深度睡眠比例
- REM睡眠
- 睡眠连续性

### 4. **身体准备度**
- 基于以上所有指标的综合分数
- >85: 适合高强度训练
- 70-85: 中等强度
- <70: 建议休息

---

## 🔗 API版本说明

- **当前使用：** Oura API V2
- **认证方式：** Personal Access Token (PAT)
- ⚠️ **注意：** PAT将在2025年底弃用，之后需要使用OAuth 2.0

---

## 📞 后续步骤

1. **获取Access Token** 并运行首次同步
2. **查看生成的报告** 在 `OuraData/Reports/` 目录
3. **告诉我同步完成**，我会帮您分析数据
4. **设置定期同步** 确保数据持续更新

---

## 📚 参考资料

- [Oura API V2 文档](https://cloud.ouraring.com/v2/docs)
- [Intro to the Oura API](https://partnersupport.ouraring.com/hc/en-us/articles/20949682312211-Intro-to-the-Oura-API)
- [Oura API V2 升级指南](https://partnersupport.ouraring.com/hc/en-us/articles/19907726838163-Oura-API-V2-Upgrade-Guide)

---

*设置完成后，所有对话将自动更新到健康营养记录文件中*
