# 金明健康看板 - 网页部署完整方案

**更新时间：** 2026-02-04
**部署目标：** 免费托管 + 每天11点自动推送

---

## 🎯 最佳免费部署方案

### 方案对比

| 平台 | 成本 | 免费子域名 | 自定义域名 | 推荐度 |
|------|------|-----------|-----------|--------|
| **GitHub Pages** | ✅ 完全免费 | username.github.io | ✅ 支持 | ⭐⭐⭐⭐⭐ |
| **Netlify** | ✅ 免费计划 | username.netlify.app | ✅ 支持 | ⭐⭐⭐⭐⭐ |
| **Vercel** | ✅ 免费计划 | username.vercel.app | ✅ 支持 | ⭐⭐⭐⭐ |
| **Cloudflare Pages** | ✅ 完全免费 | username.pages.dev | ✅ 支持 | ⭐⭐⭐⭐⭐ |

**推荐方案：Netlify** ⭐⭐⭐⭐⭐

**理由：**
- ✅ 完全免费（100GB带宽/月）
- ✅ 自动部署（连接GitHub仓库）
- ✅ 支持表单处理（训练日志输入）
- ✅ 免费SSL证书
- ✅ 全球CDN加速
- ✅ 支持自定义域名
- ✅ 中国用户友好

---

## 🚀 方案1：Netlify部署（推荐）⭐⭐⭐⭐⭐

### 优势
- ✅ **完全免费** - 无需信用卡
- ✅ **自动部署** - 代码推送自动更新
- ✅ **免费子域名** - yourname.netlify.app
- ✅ **自定义域名** - 可绑定自己的域名（如需要）
- ✅ **表单处理** - 支持训练日志输入功能
- ✅ **全球CDN** - 访问速度快
- ✅ **HTTPS** - 自动SSL证书

### 免费子域名选项
1. `williamjoy-health.netlify.app`
2. `jinming-health.netlify.app`
3. `williamjoy-freediving.netlify.app`

### 部署步骤

#### 步骤1：准备代码仓库（5分钟）

```bash
# 1. 创建GitHub仓库
# 访问：https://github.com/new
# 仓库名：jinming-health-dashboard
# 设为Public（公开）
# Description: 金明健康看板系统

# 2. 上传看板文件
cd /Users/williamjoy/Desktop/AI/QuantTrading/QuantTrading/Personal/Health

# 初始化git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 金明健康看板系统"

# 添加远程仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/jinming-health-dashboard.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

#### 步骤2：连接Netlify（3分钟）

1. 访问：https://app.netlify.com/start
2. 选择 "Deploy from Git repository"
3. 选择 GitHub，授权登录
4. 选择 `jinming-health-dashboard` 仓库
5. 构建命令：留空（自动检测）
6. 发布目录：留空（根目录）
7. 点击 "Deploy Site"

**等待1-2分钟，网站即可发布！**

#### 步骤3：访问网站

**免费子域名：**
- 自动生成的域名：`https://random-name.netlify.app`
- 可在Netlify后台修改为：`williamjoy-health.netlify.app`

#### 步骤4：设置自动部署

**已配置：**
- GitHub仓库有更新时自动触发部署
- 无需手动操作，代码推送后1-2分钟自动上线

---

## 🌐 方案2：GitHub Pages（完全免费）⭐⭐⭐⭐⭐

### 优势
- ✅ **100%免费** - 永久免费
- ✅ **GitHub Pages子域名** - `username.github.io`
- ✅ **支持自定义域名**
- ✅ **自动HTTPS**
- ✅ **无限带宽**

### 免费子域名
- `williamjoy.github.io`（如果用户名是williamjoy）
- 或 `jinming-health.github.io`

### 部署步骤

#### 步骤1：创建GitHub仓库
同方案1

#### 步骤2：配置GitHub Pages
1. 进入仓库设置
2. 点击 "Pages"
3. Source: Deploy from a branch
4. Branch: main
5. Folder: / (root)
6. 点击 "Save"

**等待1-2分钟，网站发布在：**
- `https://williamjoy.github.io/jinming-health-dashboard/`

---

## 💰 域名购买方案（如果需要自定义域名）

### 顶级域名价格（2024年）

| 域名 | 首年价格 | 续费价格 | 推荐度 |
|------|----------|----------|--------|
| **.com** | $10-15 | $10-15 | ⭐⭐⭐⭐⭐ |
| **.xyz** | $1-2 | $1-2 | ⭐⭐⭐⭐ 最便宜 |
| **.top** | $1-2 | $1-2 | ⭐⭐⭐⭐ |
| **.site** | $2-3 | $2-3 | ⭐⭐⭐⭐ |
| **.health** | $20-30 | $20-30 | ⭐⭐⭐ 专业 |
| **.fitness** | $15-25 | $15-25 | ⭐⭐⭐ |
| **.freediving** | $15-25 | $15-25 | ⭐⭐⭐ 最相关 |

**推荐：**
- 最便宜：`.xyz` (约$1-2/年)
- 最专业：`.com` (约$10-15/年)
- 最相关：`.health` 或 `.fitness`

**域名注册商：**
- Namecheap
- GoDaddy
- 阿里云
- 腾讯云

---

## 📝 每天11点推送系统

### 方案1：GitHub Actions自动化推送

#### 实现方式

1. **创建GitHub Actions工作流**
   - 每天11:00自动运行
   - 运行 `ultimate_dashboard.py`
   - 更新数据
   - 自动部署到Netlify

#### 配置文件

创建 `.github/workflows/daily-update.yml`：

```yaml
name: Daily Health Update

on:
  schedule:
    - cron: '0 3 * * *'  # UTC 3:00 = 北京11:00
  workflow_dispatch:  # 支持手动触发

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install pandas requests
        # 安装其他依赖...

    - name: Run health dashboard
      env:
        OURA_ACCESS_TOKEN: ${{ secrets.OURA_ACCESS_TOKEN }}
      run: |
        python ultimate_dashboard.py

    - name: Commit and push
      run: |
        git config --local user.email "actions@github.com"
        git config --local user.name "GitHub Actions"
        git add .
        git commit -m "Auto: Daily health update $(date +'%Y-%m-%d')"
        git push
```

### 方案2：服务器定时任务

如果使用自己的服务器：

```bash
# 添加crontab
crontab -e

# 添加以下行
0 11 * * * cd /path/to/Personal/Health && python3 ultimate_dashboard.py && git add . && git commit -m "Auto update" && git push
```

---

## 📋 完整部署检查清单

### 部署前检查
- [ ] 确认所有文件在本地仓库
- [ ] 测试本地看板是否正常
- [ ] 检查API密钥安全性
- [ ] 移除敏感信息（API密钥等）
- [ ] 测试所有超链接是否有效
- [ ] 验证图表路径正确

### 部署步骤
- [ ] 创建GitHub仓库
- [ ] 上传所有文件到GitHub
- [ ] 连接Netlify（或选择其他平台）
- [ ] 测试网站访问
- [ ] 配置自定义域名（可选）
- [ ] 设置自动部署
- [ ] 测试自动推送

### 部署后验证
- [ ] 所有页面可访问
- [ ] 8个图表正确显示
- [ ] 训练日志输入功能正常
- [ ] PB数据显示正确
- [ ] 近期目标Section显示
- [ ] 推送系统测试

---

## 🔧 技术要求

### 文件结构

```
Personal/Health/
├── index.html                      # 主页（入口）
├── log_input_local.html            # 训练日志输入
├── ultimate_dashboard.py            # 主系统脚本
├── pool_training_advisor.py         # 训练顾问
└── DailyReports/                    # 所有生成的报告
    ├── dashboard_2026-02-04.html
    ├── super_dashboard.html
    ├── dashboard_with_charts.html
    └── charts/                        # 8个图表
```

### 静态网站要求
- ✅ 纯HTML/CSS/JavaScript
- ✅ 无后端服务器依赖
- ✅ 所有数据通过API或静态JSON获取
- ✅ 响应式设计

### 数据更新机制
1. **自动更新**：每天11点运行 `ultimate_dashboard.py`
2. **手动更新**：运行脚本生成新报告
3. **数据存储**：本地JSON + 训练日志系统

---

## 📊 成本对比

### 方案1：完全免费（推荐）

**域名：** username.netlify.app（免费）
**托管：** Netlify免费计划（100GB/月）
**SSL证书：** 免费（Let's Encrypt）
**总计：** **$0/年** ✅

### 方案2：便宜付费域名

**域名：** .xyz ($1-2/年)
**托管：** Netlify免费
**SSL证书：** 免费
**总计：** **$1-2/年** ✅

### 方案3：专业域名

**域名：** .com ($10-15/年)
**托管：** Netlify免费
**SSL证书：** 免费
**总计：** **$10-15/年** ✅

---

## 🎯 推荐域名名称

### 基于名字
- `williamjoy-health.netlify.app`
- `jinming-health.netlify.app`

### 基于健康
- `jinming-dashboard.netlify.app`
- `health-tracker.netlify.app`
- `freediving-dashboard.netlify.app`

### 购买域名
- `williamjoy.xyz` ($1-2/年)
- `jinming.health` ($20-30/年)
- `jinming.fitness` ($15-25/年)
- `jinming.freediving` ($15-25/年)

---

## ⚡ 快速开始（10分钟部署）

### 使用Netlify部署

1. **准备代码** (3分钟)
```bash
cd /Users/williamjoy/Desktop/AI/QuantTrading/QuantTrading/Personal/Health
git init
git add .
git commit -m "Initial commit"
```

2. **创建GitHub仓库** (2分钟)
- 访问 https://github.com/new
- 创建新仓库 `jinming-health-dashboard`
- 上传代码（通过Web界面上传或git push）

3. **连接Netlify** (3分钟)
- 访问 https://app.netlify.com/start
- 选择GitHub仓库
- 点击Deploy

4. **访问网站** (1分钟)
- 自动生成的域名：`random-name.netlify.app`
- 修改为：`williamjoy-health.netlify.app`

5. **完成！**
- 网站已上线
- 访问：`https://williamjoy-health.netlify.app`

---

## 📚 参考资源

- [GitHub Pages官方文档](https://docs.github.com/zh/pages/configuring-a-custom-domain-for-your-pages-site/)
- [Netlify官方文档](https://docs.netlify.com/)
- [2024免费网站部署平台测评](https://juejin.cn/post/7438822895227256832)
- [免费好用的静态网页托管平台对比](https://blog.csdn.net/m0_74412436/article/details/143998746)
- [Netlify免费部署教程](https://blog.csdn.net/shaoyezhangliwei/article/details/146191022)

---

## 📝 README更新内容

### 添加到项目README

```markdown
## 🌐 在线访问

**网站地址：** https://williamjoy-health.netlify.app

**部署平台：** Netlify（免费托管）

**更新频率：** 每天11:00自动更新

## 🔄 自动更新

- ✅ 每天11:00自动运行数据更新
- ✅ 自动部署到网站
- ✅ 无需手动操作

## 🛠️ 本地运行

```bash
cd Personal/Health
python3 ultimate_dashboard.py
```

## 📝 数据备份

- 训练日志：本地localStorage + JSON导出
- 健康数据：每日自动生成
- 图表文件：DailyReports/charts/
```

---

**状态：✅ 部署方案已准备完毕**

*最后更新：2026-02-04*
*推荐方案：Netlify免费托管*
