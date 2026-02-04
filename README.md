# 🏊 金明健康看板系统

**版本：** v4.0
**最后更新：** 2026-02-04
**在线访问：** https://williamjoy-health.netlify.app

---

## 📋 项目简介

这是一个专为自由潜水世界纪录保持者设计的综合健康看板系统，整合Oura Ring数据、天气、空气质量、训练建议、饮食计划等功能。

### 核心功能
- ✅ 每日健康评分（准备度、睡眠、活动）
- ✅ 实时天气和空气质量
- ✅ 完整训练建议（泳池训练+陆地训练）
- ✅ 两餐饮食计划（含营养表格）
- ✅ 补剂清单和管理
- ✅ 8个专业数据可视化图表
- ✅ 训练日志输入系统
- ✅ 个人最好成绩（PB）管理
- ✅ 近期目标追踪（CWT 80米 + Mouthfill 3.0）

---

## 🌐 在线访问

### 主网站
**网址：** https://william-health.netlify.app
**部署平台：** Netlify（免费托管）
**更新频率：** 每天11:00自动更新

### 备用链接
- GitHub Pages: https://williamjoy.github.io/jinming-health-dashboard/
- Netlify备用: https://app.netlify.com/sites/williamjoy-health

---

## 🚀 快速开始

### 本地运行

```bash
cd Personal/Health
python3 ultimate_dashboard.py
```

**生成内容：**
- `DailyReports/dashboard_YYYY-MM-DD.html` - 完整HTML看板
- `DailyReports/dashboard_YYYY-MM-DD.md` - Markdown报告（1010行）
- `DailyReports/charts/` - 8个专业图表
- `DailyReports/super_dashboard.html` - 超级增强看板
- `DailyReports/dashboard_with_charts.html` - 专业可视化看板
- `DailyReports/dashboard_visual_YYYY-MM-DD.html` - 可视化看板

### 训练日志输入

```bash
# 方式1：本地版本（推荐，无需服务器）
open log_input_local.html

# 方式2：服务器版本（需要安装Flask）
python3 log_server.py
# 访问：http://localhost:5000
```

---

## ⚠️ 重要提醒：每天11点必须推送

### 🚨 死命令 #1：每天11点自动推送

**要求：**
- ✅ 每天11:00（北京时间）必须运行健康看板更新
- ✅ 更新后自动推送到GitHub仓库
- ✅ Netlify自动检测更新并部署
- ✅ 确保在线网站始终是最新数据

**自动化方式：**
- **GitHub Actions**：已配置 `.github/workflows/daily-update.yml`
- 每天11:00自动运行
- 无需手动操作

**手动方式（备选）：**
```bash
cd Personal/Health
python3 ultimate_dashboard.py
git add .
git commit -m "Manual update: $(date +'%Y-%m-%d')"
git push
```

**推送到GitHub后，Netlify会自动检测并在1-2分钟内更新网站。**

### 🔍 推送前检查清单

**每次推送前必须检查：**

1. **API密钥检查**
   - [ ] Oura API Token有效
   - [ ] 天气API密钥有效
   - [ ] 空气质量API密钥有效

2. **数据完整性检查**
   - [ ] 所有图表路径正确
   - [ ] 所有超链接可访问
   - [ ] 训练建议内容完整
   - [ ] PB数据显示正确
   - [ ] 近期目标Section存在

3. **文件检查**
   - [ ] `index.html` - 主页入口
   - [ ] `log_input_local.html` - 日志输入
   [ ] `DailyReports/charts/` - 8个图表
   - [ ] `DailyReports/*.html` - 所有HTML看板
   - [ ] `DailyReports/*.md` - Markdown报告

4. **功能检查**
   - [ ] 训练日志输入功能正常
   - [ ] PB更新功能正常
   - [ ] 肺活量记录功能正常
   - [ ] 数据导出/导入功能正常

5. **链接验证**
   - [ ] 检查所有超链接
   - [ ] 测试图表加载
   - [ ] 验证数据库连接

---

## 📂 项目结构

```
Personal/Health/
├── index.html                          # 🏠 主页入口
├── log_input_local.html                # 📝 训练日志输入系统
├── ultimate_dashboard.py               # 🚀 主系统脚本
├── pool_training_advisor.py            # 🏊 泳池训练顾问
├── training_log_manager.py             # 📋 训练日志管理器
├── enhanced_visualizer.py              # 📊 增强可视化模块
├── auto_update_service.py              # 🔄 自动更新服务
├── DEPLOYMENT_GUIDE.md                 # 📚 部署指南
├── DEAD_COMMANDS_AND_REQUIREMENTS.md    # ⚠️ 死命令文档
├── USER_CONTEXT.md                     # 👤 用户上下文
├── ALL_TRAINING_NOTES.md               # 📖 所有训练笔记
├── RECENT_GOALS_AND_TRAINING_PLAN.md   # 🎯 近期目标与训练计划
│
├── .github/
│   └── workflows/
│       └── daily-update.yml            # ⏰ GitHub Actions工作流（每天11点运行）
│
├── DailyReports/                        # 📊 生成的报告
│   ├── dashboard_2026-02-04.html       # 基础HTML看板
│   ├── dashboard_visual_2026-02-04.html # 可视化看板
│   ├── dashboard_with_charts.html      # 专业可视化看板
│   ├── super_dashboard.html            # 超级增强看板
│   ├── dashboard_2026-02-04.md         # Markdown报告（1010行）
│   └── charts/                            # 图表文件夹（8个图表）
│       ├── readiness_radar.png
│       ├── sleep_quality.png
│       ├── activity_distribution.png
│       ├── readiness_gauge.png
│       ├── 30_day_trends.png
│       ├── sleep_quality_distribution.png
│       ├── nutrition_visualization.png
│       └── readiness_comprehensive.png
│
└── TrainingLogs/                        # 📋 训练数据
    ├── training_logs.json              # 训练日志
    ├── lung_capacity.json              # 肺活量数据（50条记录）
    └── personal_best.json              # 个人最好成绩
```

---

## 🔑 API配置

### Oura Ring API V2

**获取Personal Access Token：**
1. 访问：https://cloud.ouraring.com/personal-access-tokens
2. 创建新Token
3. 设置环境变量：
```bash
export OURA_ACCESS_TOKEN='your_token_here'
```

### 天气API
- **和风天气：** https://www.qweather.com/
- **Open-Meteo：** https://open-meteo.com/

### 空气质量API
- **WAQI.info：** https://waqi.info/
- **AQICN：** https://aqicn.org/

---

## 🎯 训练限制（死命令）

### ⚠️ 重要限制
- **日常训练建议只提泳池训练和陆地训练**
- **绝对禁止提及"深度训练"**
- **不使用CWT、CNF、DYN、DNF术语**（泳池训练时）
- **只提：无蹼、单蹼、双蹼、静态闭气、1000米蛙泳**

---

## 📊 可视化图表

### Matplotlib图表（8个）
1. readiness_radar.png - 健康指标雷达图
2. sleep_quality.png - 睡眠质量柱状图
3. activity_distribution.png - 活动分布饼图
4. readiness_gemplate.png - 训练准备度仪表盘
5. 30_day_trends.png - 30天健康趋势分析
6. sleep_quality_distribution.png - 睡眠质量深度分析
7. nutrition_visualization.png - 营养摄入分析
8. readiness_comprehensive.png - 准备度综合分析

### Chart.js交互图表（6个）
1. 准备度趋势图（7天）
2. 睡眠质量趋势（7天）
3. 活动分布图
4. 训练强度趋势
5. HRV变化趋势
6. 静息心率趋势

---

## 🏆 个人最好成绩（PB）

### 泳池成绩
- DNF（无蹼动态）：212米
- DYN（动态有蹼）：319米
- DYNB（双蹼动态）：287米
- STA（静态闭气）：9分08秒

### 肺活量
- PB：7962ml

### 陆地测试
- 123挑战：13分27秒
- 空肺深蹲：83个

---

## 🎯 近期目标

### 目标1：CWT深度80米
- 训练重点：逐步递增（60→70→80米）
- 在42米深池模拟训练
- 强化Mouthfill应用

### 目标2：Mouthfill效率3.0
- 充气速度：≤ 3秒
- 充气量：≥ 90%口腔容量
- 控制力：无泄漏
- 可重复性：≥ 3次/潜

### 详细训练计划
- **完整文档：** `RECENT_GOALS_AND_TRAINING_PLAN.md`
- **场馆：** 中国水之极42米深池
- **时间：** 本周末（周五-周日）

---

## 📝 更新日志

### v4.0 (2026-02-04)
- ✅ 添加"近期目标"Section
- ✅ 更新个人最好成绩（PB）结构
- ✅ 移除深度项目（CWT、CNF等）
- ✅ 添加陆地测试成绩
- ✅ 配置GitHub Actions自动推送
- ✅ 完整部署指南

### v3.1 (2026-02-04)
- ✅ 训练日志输入系统
- ✅ 肺活量数据导入（50条记录）
- ✅ PB管理功能

### v3.0 (2026-02-04)
- ✅ 8个matplotlib图表
- ✅ 1010行完整建议
- ✅ 多个HTML版本

---

## 📚 相关文档

- [DEAD_COMMANDS_AND_REQUIREMENTS.md](DEAD_COMMANDS_AND_REQUIREMENTS.md) - 死命令和需求文档
- [USER_CONTEXT.md](USER_CONTEXT.md) - 用户上下文
- [ALL_TRAINING_NOTES.md](ALL_TRAINING_NOTES.md) - 所有训练笔记
- [TRAINING_LOG_GUIDE.md](TRAINING_LOG_GUIDE.md) - 训练日志使用指南
- [RECENT_GOALS_AND_TRAINING_PLAN.md](RECENT_GOALS_AND_TRAINING_PLAN.md) - 近期目标与训练计划
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 网页部署完整方案

---

## 🤖 技术栈

### 后端
- Python 3.9+
- pandas（数据处理）
- requests（API调用）
- openpyxl（Excel处理）

### 前端
- HTML5/CSS3
- JavaScript（ES6+）
- Chart.js（交互图表）
- Matplotlib（专业图表）

### 部署
- GitHub（代码托管）
- Netlify（静态托管）
- GitHub Actions（CI/CD）

---

## 📧 联系方式

**开发者：** Claude Sonnet 4.5
**项目所有者：** 金明（William Joy）
**最后更新：** 2026-02-04

---

## 📄 许可证

MIT License

Copyright (c) 2026 金明

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 🎉 使用说明

### 1. 本地查看
```bash
# 打开主页
open index.html

# 或打开日志输入系统
open log_input_local.html
```

### 2. 在线访问
访问：https://william-health.netlify.app

### 3. 数据更新
每天11:00自动更新，无需手动操作

### 4. 添加训练日志
访问在线网站，点击"训练日志输入系统"

---

**⚠️ 重要：每天11点必须检查并推送更新！**

*最后更新：2026-02-04*
*在线地址：https://william-health.netlify.app*
