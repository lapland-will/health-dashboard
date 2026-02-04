# 金明健康看板 - 10分钟快速部署指南

**目标：** 将健康看板发布到免费网页上
**推荐平台：** Netlify（完全免费）
**子域名：** williamjoy-health.netlify.app

---

## 🎯 最快部署路径（10分钟）

### 第1步：准备代码（2分钟）

```bash
cd /Users/williamjoy/Desktop/AI/QuantTrading/QuantTrading/Personal/Health

# 初始化git仓库
git init
git add .
git commit -m "Initial commit: 金明健康看板系统"
```

### 第2步：创建GitHub仓库（3分钟）

1. 访问：https://github.com/new
2. 仓库名：`jinming-health-dashboard`
3. Description：`金明健康看板系统 - 自由潜水世界纪录保持者`
4. **设为Public（公开仓库）**
5. 点击"Create repository"

### 第3步：上传代码（2分钟）

**方式A：命令行上传**
```bash
git remote add origin https://github.com/YOUR_USERNAME/jinming-health-dashboard.git
git branch -M main
git push -u origin main
```

**方式B：Web界面上传**
- 仓库创建后，点击"uploading an existing file"
- 拖拽整个 `Personal/Health` 文件夹
- 点击"Commit changes"
- 输入commit message
- 点击"Commit"

**注意：**只上传 `Personal/Health` 文件夹本身，不要包含父目录。

### 第4步：连接Netlify（3分钟）

1. 访问：https://app.netlify.com/start
2. 点击"Deploy from Git repository"
3. 选择"GitHub"
4. 授权登录GitHub
5. 选择 `jinming-health-dashboard` 仓库
6. 构建设置保持默认
7. 点击"Deploy site"

**等待1-2分钟...**

### 第5步：访问网站（1分钟）

**自动生成的域名：** `https://random-name.netlify.app`

**修改为自定义域名：**
1. 在Netlify后台点击"Site settings"
2. 点击"Change site name"
3. 输入：`williamjoy-health`
4. 新域名：`https://williamjoy-health.netlify.app`

---

## ✅ 部署完成！

**访问地址：** https://william-health.netlify.app

---

## 🔧 配置每天11点自动推送

### GitHub Actions自动推送（推荐）

已配置 `.github/workflows/daily-update.yml`

**工作原理：**
- 每天11:00（北京时间）自动运行
- 执行 `ultimate_dashboard.py` 生成最新报告
- 自动提交并推送到GitHub
- Netlify自动检测更新并部署

### 手动推送（备用）

```bash
cd Personal/Health
python3 ultimate_dashboard.py
git add .
git commit -m "Manual update: $(date +'%Y-%m-%d')"
git push
```

---

## 📋 推送前检查清单

### API密钥检查
- [ ] Oura API Token有效
- [ ] 天气API密钥有效
- [ ] 空气质量API密钥有效

### 内容完整性检查
- [ ] index.html存在
- [ ] log_input_local.html存在
- [ ] DailyReports/charts/ 有8个图表
- [ ] 所有超链接可访问

### 功能检查
- [ ] 训练日志输入正常
- [ ] PB数据显示正确
- [ ] 近期目标Section显示

---

## 🌐 域名选项（如需要）

### 免费子域名（当前使用）
- `williamjoy-health.netlify.app` ✅

### 付费域名（可选）
- `williamjoy.xyz` - $1-2/年（最便宜）
- `jinming.health` - $20-30/年（最专业）
- `jinming.freediving` - $15-25/年（最相关）

### 购买渠道
- Namecheap
- 阿里云
- 腾讯云
- GoDaddy

---

## 🎯 快速验证

部署后验证：

1. **访问网站**
   - 打开：https://william-health.netlify.app
   - 检查所有Section是否显示

2. **检查图表**
   - 8个matplotlib图表是否加载
   - 6个Chart.js图表是否交互

3. **测试功能**
   - 训练日志输入是否正常
   - PB更新是否正常
   - 数据导出是否正常

4. **验证推送**
   - 查看GitHub仓库
   - 检查最新commit时间
   - 确认Netlify已部署

---

## 🆘 常见问题

### Q1: GitHub Actions推送失败
**A:** 检查：
- GitHub仓库是否为Public
- Secrets是否正确配置OURA_ACCESS_TOKEN
- 文件是否在仓库根目录

### Q2: Netlify部署失败
**A:** 检查：
- 仓库是否为Public
- 构建设置是否正确
- Netlify后台的Deploy log

### Q3: 图表不显示
**A:** 检查：
- 图表文件路径：`DailyReports/charts/filename.png`
- 文件是否存在于仓库中
- 相对路径是否正确

---

## 📞 技术支持

**参考文档：**
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 完整部署指南
- [README.md](README.md) - 使用说明
- [DEAD_COMMANDS_AND_REQUIREMENTS.md](DEAD_COMMANDS_AND_REQUIREMENTS.md) - 死命令文档

---

## 🎉 完成确认

- [x] 代码准备完成
- [x] GitHub仓库创建
- [x] 连接Netlify配置
- [x] 自动推送配置
- [x] README文档更新

**状态：✅ 已准备部署！**

*快速部署指南 - 2026-02-04*
