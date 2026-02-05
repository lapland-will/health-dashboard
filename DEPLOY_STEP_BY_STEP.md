# 金明健康看板 - 部署操作指南

**当前状态：** Git仓库已初始化，所有文件已提交
**目标：** 部署到免费网站并配置每天11点自动更新

---

## 📋 第1步：创建GitHub仓库（5分钟）

### 方法A：通过Web界面创建（推荐）

1. **打开GitHub创建页面**
   - 点击下面的链接直接打开：
   - https://github.com/new

2. **填写仓库信息**
   - Repository name: `jinming-health-dashboard`
   - Description: `金明健康看板系统 - 自由潜水世界纪录保持者`
   - **重要：选择 Public（公开仓库）** ✅
   - **不要勾选** "Add a README file"
   - **不要勾选** "Add .gitignore"
   - **不要勾选** "Choose a license"

3. **点击 "Create repository"**

### 方法B：通过命令行（需要安装gh CLI）

如果您的系统安装了GitHub CLI：
```bash
gh repo create jinming-health-dashboard --public --description "金明健康看板系统 - 自由潜水世界纪录保持者"
```

---

## 📤 第2步：推送代码到GitHub（3分钟）

创建GitHub仓库后，GitHub会显示命令。在终端执行：

```bash
cd /Users/williamjoy/Desktop/AI/QuantTrading/QuantTrading/Personal/Health

# 添加远程仓库（替换YOUR_USERNAME为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/jinming-health-dashboard.git

# 推送代码到GitHub
git branch -M main
git push -u origin main
```

**如果遇到用户名/密码问题：**
```bash
# 使用Personal Access Token（推荐）
# 1. 访问：https://github.com/settings/tokens
# 2. 生成新Token，选择 repo 权限
# 3. 使用Token代替密码推送
```

---

## 🌐 第3步：连接Netlify（3分钟）

1. **打开Netlify部署页面**
   - 点击：https://app.netlify.com/start

2. **选择 "Deploy from Git repository"**

3. **选择 "GitHub" 并授权登录**

4. **选择 `jinming-health-dashboard` 仓库**

5. **构建设置保持默认**
   - Build command: 留空
   - Publish directory: 留空（根目录）

6. **点击 "Deploy Site"**

**等待1-2分钟，网站将自动发布！**

---

## 🎨 第4步：设置自定义域名（1分钟）

### 免费子域名（推荐）

Netlify会自动生成一个域名，例如：
- `https://amazing-johnson-123456.netlify.app`

**修改为更好记的域名：**

1. 在Netlify后台点击 "Site settings"
2. 点击 "Change site name"
3. 输入：`williamjoy-health`
4. 新域名：`https://williamjoy-health.netlify.app`

### 其他免费域名选项

- `jinming-health.netlify.app`
- `williamjoy-freediving.netlify.app`
- `jinming-dashboard.netlify.app`

---

## 🔑 第5步：配置GitHub Actions密钥（2分钟）

为了使每天11点自动更新工作，需要配置Oura API Token：

1. **获取Ourating API Token**
   - 访问：https://cloud.ouraring.com/personal-access-tokens
   - 创建新Token
   - 复制Token

2. **在GitHub仓库中设置Secret**
   - 打开您的GitHub仓库
   - 点击 Settings → Secrets and variables → Actions
   - 点击 "New repository secret"
   - Name: `OURA_ACCESS_TOKEN`
   - Secret: 粘贴您的Oura Token
   - 点击 "Add secret"

---

## ⏰ 第6步：测试自动更新（可选）

### 手动触发GitHub Actions

1. **打开GitHub仓库的Actions页面**
   - 点击 "Actions" 标签

2. **选择 "每日健康看板自动更新" workflow**

3. **点击 "Run workflow" 按钮**

4. **选择分支：main**

5. **点击 "Run workflow" 绿色按钮**

这将测试每天11点的自动更新流程是否正常工作。

---

## ✅ 部署完成检查清单

- [ ] GitHub仓库已创建（Public）
- [ ] 代码已推送到GitHub
- [ ] Netlify已连接并部署成功
- [ ] 网站可以访问：https://williamjoy-health.netlify.app
- [ ] Oura API Token已配置到GitHub Secrets
- [ ] 测试手动触发GitHub Actions成功
- [ ] 所有页面显示正常
- [ ] 8个图表正确加载
- [ ] 训练日志输入功能正常

---

## 🌐 访问您的网站

### 主要网站
- **Netlify部署：** https://williamjoy-health.netlify.app

### 备用链接
- **GitHub仓库：** https://github.com/YOUR_USERNAME/jinming-health-dashboard
- **Netlify后台：** https://app.netlify.com/sites/williamjoy-health/overview

---

## 🔄 每天11点自动更新

### 工作流程

1. **每天11:00（北京时间）**
   - GitHub Actions自动触发

2. **运行健康看板脚本**
   - 获取Oura Ring最新数据
   - 生成新的HTML报告
   - 生成8个图表

3. **自动提交到GitHub**
   - 更新仓库文件

4. **Netlify自动部署**
   - 检测到GitHub更新
   - 1-2分钟内重新部署网站

5. **网站更新完成**
   - 无需手动操作
   - 网站始终保持最新数据

### 手动更新（备用）

如果需要手动更新：
```bash
cd Personal/Health
python3 ultimate_dashboard.py
git add .
git commit -m "Manual update: $(date +'%Y-%m-%d')"
git push
```

推送后，Netlify会在1-2分钟内自动部署。

---

## 📊 部署成功后

您将拥有：
- ✅ 完全免费的网站（$0/年）
- ✅ 自动域名：williamjoy-health.netlify.app
- ✅ 每天11点自动更新
- ✅ 全球CDN加速
- ✅ 免费SSL证书
- ✅ 训练日志输入系统
- ✅ 8个专业数据可视化图表
- ✅ 完整的健康看板系统

---

## 🆘 常见问题

### Q1: Git推送失败
**A:**
- 检查GitHub仓库是否为Public
- 确认远程仓库URL正确
- 使用Personal Access Token代替密码

### Q2: Netlify部署失败
**A:**
- 检查仓库是否为Public
- 查看Netlify的Deploy log
- 确认index.html在仓库根目录

### Q3: GitHub Actions失败
**A:**
- 检查OURA_ACCESS_TOKEN是否正确配置
- 查看Actions的运行日志
- 确认所有Python依赖已安装

### Q4: 图表不显示
**A:**
- 检查DailyReports/charts/文件夹
- 确认图表文件路径正确
- 运行ultimate_dashboard.py重新生成

---

## 📞 需要帮助？

**参考文档：**
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 完整部署指南
- [DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md) - 10分钟快速部署
- [README.md](README.md) - 使用说明

**在线支持：**
- Netlify文档：https://docs.netlify.com/
- GitHub Actions文档：https://docs.github.com/en/actions

---

## 🎉 开始部署！

**现在开始第1步：点击下面链接创建GitHub仓库**

👉 **https://github.com/new**

---

*部署操作指南 - 2026-02-04*
*准备状态：✅ Git仓库已初始化*
*下一步：创建GitHub仓库*
