# 华为Health Kit API对接指南

**更新时间：** 2025-01-31
**目标设备：** 华为WATCH Ultimate 2
**目标：** 整合健康数据到健康记录系统

---

## 📋 对接方式对比

| 方式 | 难度 | 时间成本 | 数据完整度 | 推荐度 |
|------|------|----------|------------|--------|
| **手动CSV导出** | ⭐ 简单 | 5-10分钟 | 80% | ✓⭐⭐⭐⭐⭐ 推荐 |
| **Health Kit API** | ⭐⭐⭐⭐⭐ 困难 | 1-2周 | 100% | ⚠️ 需企业资质 |

---

## 🚀 方式一：手动CSV导出（推荐 - 立即可用）

### 优势
- ✓ 无需开发者账号
- ✓ 无需编写代码
- ✓ 立即可获取数据
- ✓ 支持所有健康数据类型

### 导出步骤

#### 1. 血压数据导出
```
1. 打开华为运动健康App（确保版本≥16.0.12.300）
2. 进入"健康"页面
3. 点击"血压"卡片
4. 点击右上角"导出"图标（或"..."菜单）
5. 选择时间范围：过去30天
6. 选择导出格式：CSV
7. 分享到备忘录或邮件
8. 保存到：Personal/Health/HuaweiData/HealthData/
```

#### 2. 其他健康数据
```
1. 打开华为运动健康App
2. 进入"我的"页面
3. 点击个人头像
4. 进入"账号与安全"或"隐私中心"
5. 选择"数据管理"或"请求副本数据"
6. 勾选"运动健康服务"
7. 等待邮件通知（约7天）
8. 下载完整数据副本
```

#### 3. 潜水数据导出
```
1. 打开华为运动健康App
2. 进入"运动"页面
3. 找到潜水记录
4. 点击具体潜水记录
5. 点击"分享"或"导出"
6. 保存到：Personal/Health/HuaweiData/DiveLogs/
```

### 数据整合

导出数据后，运行整合脚本：
```bash
cd ~/Desktop/AI/QuantTrading/QuantTrading/Personal/Health
python3 huawei_oura_integration.py
```

---

## 🔐 方式二：Health Kit API对接（需企业资质）

### 前置要求

#### 1️⃣ 必须具备的条件
- **企业开发者账号**（个人账号无法申请）
- **企业营业执照**
- **AppGallery Connect项目**
- **应用审核通过**

#### 2️⃣ 注册流程

**步骤1：注册华为开发者账号**
```
1. 访问：https://developer.huawei.com/
2. 点击"注册"
3. 选择"企业开发者"
4. 准备材料：
   - 企业营业执照
   - 法人身份证
   - 企业邮箱
   - 联系电话
5. 提交审核（1-3个工作日）
```

**步骤2：创建应用**
```
1. 登录AppGallery Connect：https://developer.huawei.com/consumer/cn/service/josp/agc/index.html
2. 创建新项目
3. 在项目中添加应用
4. 选择应用平台（Android/iOS/Web）
5. 填写应用信息
   - 应用名称
   - 应用包名（如：com.health.freediving）
   - 应用类别：健康与健身
```

**步骤3：开通Health Kit服务**
```
1. 进入项目设置
2. 选择"API管理"
3. 找到"Health Kit"或"健康服务"
4. 点击"开通服务"
5. 阅读并同意服务协议
6. 提交审核（需要说明应用场景）
```

**步骤4：申请数据权限**
```
需要申请的数据权限：
- HEALTH_CP_HEART_RATE（心率）
- HEALTH_CP_BLOOD_PRESSURE（血压）
- HEALTH_CP_SLEEP（睡眠）
- HEALTH_CP_STEP_COUNT（步数）
- HEALTH_CP_CALORIE（卡路里）
- HEALTH_CP_DISTANCE（距离）

注意：敏感数据（如血压）需要额外审核
```

**步骤5：等待审核**
```
审核时间：1-2周
审核标准：
- 应用场景说明
- 隐私政策
- 数据使用说明
- 用户授权流程
```

### API密钥和凭证生成

#### 1. 获取Client ID和Client Secret
```
1. 登录AppGallery Connect
2. 进入你的项目
3. 选择"我的应用"
4. 选择"开发" → "配置"
5. 查看以下信息：
   - Client ID
   - Client Secret
   - App ID
   - Package Name
```

#### 2. 配置OAuth 2.0
```
授权模式：Authorization Code
授权端点：https://oauth-login.cloud.huawei.com/oauth2/v3/authorize
Token端点：https://oauth-login.cloud.huawei.com/oauth2/v3/token
```

#### 3. 设置SHA256指纹
```
1. 使用keytool生成SHA256指纹：
   keytool -list -v -keystore your_keystore.jks

2. 在AppGallery Connect中添加SHA256指纹
3. 这是为了验证应用身份
```

### 认证流程

华为Health Kit使用OAuth 2.0授权码模式：

#### 1. 用户授权
```python
# 构建授权URL
auth_url = (
    f"https://oauth-login.cloud.huawei.com/oauth2/v3/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope={SCOPES}"
    f"&state={random_state}"
)

# 用户访问此URL并授权
# 授权后会被重定向到redirect_uri，并携带授权码
```

#### 2. 获取Access Token
```python
# 使用授权码换取access token
token_url = "https://oauth-login.cloud.huawei.com/oauth2/v3/token"

data = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI
}

response = requests.post(token_url, data=data)
access_token = response.json()["access_token"]
refresh_token = response.json()["refresh_token"]
```

#### 3. 刷新Token（Access Token有效期1小时）
```python
# 使用refresh_token刷新
data = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

response = requests.post(token_url, data=data)
new_access_token = response.json()["access_token"]
```

### API调用示例

```python
#!/usr/bin/env python3
"""
华为Health Kit API调用示例
需要先完成OAuth 2.0认证
"""

import requests
import json
from datetime import datetime, timedelta

class HuaweiHealthKitAPI:
    def __init__(self, access_token):
        self.base_url = "https://health.huawei.com/cloud/hhi/api"
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def get_health_data(self, data_type, start_date, end_date):
        """
        获取健康数据
        :param data_type: 数据类型（如：HEALTH_CP_HEART_RATE）
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        """
        url = f"{self.base_url}/healthdata/data/query"

        payload = {
            "dataType": data_type,
            "startTime": f"{start_date}T00:00:00Z",
            "endTime": f"{end_date}T23:59:59Z",
            "pageIndex": 1,
            "pageSize": 1000
        }

        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def get_blood_pressure(self, days=30):
        """获取血压数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_health_data(
            data_type="HEALTH_CP_BLOOD_PRESSURE",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

    def get_heart_rate(self, days=30):
        """获取心率数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_health_data(
            data_type="HEALTH_CP_HEART_RATE",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

    def get_sleep_data(self, days=30):
        """获取睡眠数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_health_data(
            data_type="HEALTH_CP_SLEEP",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

# 使用示例
if __name__ == "__main__":
    # 从OAuth 2.0流程获取的access_token
    ACCESS_TOKEN = "your_access_token_here"

    api = HuaweiHealthKitAPI(ACCESS_TOKEN)

    # 获取血压数据
    bp_data = api.get_blood_pressure(days=30)
    print("血压数据：", json.dumps(bp_data, indent=2, ensure_ascii=False))

    # 获取心率数据
    hr_data = api.get_heart_rate(days=30)
    print("心率数据：", json.dumps(hr_data, indent=2, ensure_ascii=False))
```

### 完整对接脚本

创建文件：`huawei_healthkit_api.py`

```python
#!/usr/bin/env python3
"""
华为Health Kit API完整对接脚本
包含OAuth 2.0认证和数据获取
"""

import requests
import json
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime, timedelta

# 配置信息（需要在AppGallery Connect获取）
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
REDIRECT_URI = "http://localhost:8000/callback"
SCOPE = "openid https://www.huawei.com/healthkit/healthdata.read"

class HuaweiAuthHandler(BaseHTTPRequestHandler):
    """处理OAuth回调"""

    def do_GET(self):
        if self.path.startswith("/callback"):
            # 解析授权码
            query = self.path.split("?", 1)[1]
            params = dict(param.split("=") for param in query.split("&"))
            auth_code = params.get("code")

            # 返回授权成功页面
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization Successful! You can close this window.</h1>")

            # 保存授权码
            with open("huawei_auth_code.txt", "w") as f:
                f.write(auth_code)

            print(f"\n✓ 授权码已保存: {auth_code}")

class HuaweiHealthKitIntegrator:
    """华为Health Kit整合器"""

    def __init__(self):
        self.auth_url = "https://oauth-login.cloud.huawei.com/oauth2/v3/authorize"
        self.token_url = "https://oauth-login.cloud.huawei.com/oauth2/v3/token"
        self.api_url = "https://health.huawei.com/cloud/hhi/api"
        self.access_token = None
        self.refresh_token = None

    def authorize(self):
        """步骤1：发起用户授权"""
        state = secrets.token_urlsafe(16)

        auth_params = {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "state": state
        }

        auth_url = f"{self.auth_url}?{self._encode_params(auth_params)}"

        print("=" * 60)
        print("华为Health Kit授权")
        print("=" * 60)
        print(f"\n请在浏览器中完成授权：\n")
        print(f"{auth_url}\n")
        print("等待授权回调...")

        # 启动本地服务器接收回调
        webbrowser.open(auth_url)
        self._start_callback_server()

    def _start_callback_server(self):
        """启动回调服务器"""
        server = HTTPServer(("localhost", 8000), HuaweiAuthHandler)
        server.handle_request()

    def get_access_token(self, auth_code):
        """步骤2：使用授权码获取access token"""
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI
        }

        response = requests.post(self.token_url, data=data)
        result = response.json()

        if "access_token" in result:
            self.access_token = result["access_token"]
            self.refresh_token = result["refresh_token"]

            # 保存凭证
            credentials = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
            }

            with open("huawei_credentials.json", "w") as f:
                json.dump(credentials, f, indent=2)

            print("✓ Access Token获取成功")
            print(f"✓ 凭证已保存到 huawei_credentials.json")

            return True
        else:
            print("❌ 获取Access Token失败：")
            print(json.dumps(result, indent=2))
            return False

    def refresh_access_token(self):
        """刷新access token"""
        # 从文件读取refresh_token
        try:
            with open("huawei_credentials.json", "r") as f:
                credentials = json.load(f)
                refresh_token = credentials["refresh_token"]
        except:
            print("❌ 未找到refresh_token，需要重新授权")
            return False

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

        response = requests.post(self.token_url, data=data)
        result = response.json()

        if "access_token" in result:
            self.access_token = result["access_token"]
            print("✓ Access Token刷新成功")
            return True
        else:
            print("❌ 刷新失败：", result)
            return False

    def sync_data(self, days=30):
        """同步健康数据"""
        if not self.access_token:
            print("❌ 请先完成授权")
            return

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 获取各类健康数据
        data_types = [
            ("HEALTH_CP_HEART_RATE", "心率"),
            ("HEALTH_CP_BLOOD_PRESSURE", "血压"),
            ("HEALTH_CP_SLEEP", "睡眠"),
            ("HEALTH_CP_STEP_COUNT", "步数")
        ]

        all_data = {}

        for data_type, name in data_types:
            print(f"\n获取{name}数据...")

            payload = {
                "dataType": data_type,
                "startTime": f"{start_date.strftime('%Y-%m-%d')}T00:00:00Z",
                "endTime": f"{end_date.strftime('%Y-%m-%d')}T23:59:59Z",
                "pageIndex": 1,
                "pageSize": 1000
            }

            response = requests.post(
                f"{self.api_url}/healthdata/data/query",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                all_data[name] = data
                print(f"✓ {name}数据获取成功")

                # 保存到文件
                output_file = Path("Personal/Health/HuaweiData/HealthData") / f"{name}_{datetime.now().strftime('%Y%m%d')}.json"
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                print(f"✓ 已保存到 {output_file}")
            else:
                print(f"❌ {name}数据获取失败：{response.status_code}")
                print(response.text)

        return all_data

def main():
    """主函数"""
    integrator = HuaweiHealthKitIntegrator()

    print("华为Health Kit API对接工具")
    print("=" * 60)

    # 检查是否已有凭证
    if Path("huawei_credentials.json").exists():
        print("发现已有凭证文件")

        with open("huawei_credentials.json", "r") as f:
            credentials = json.load(f)
            expires_at = datetime.fromisoformat(credentials["expires_at"])

        if datetime.now() < expires_at:
            print("✓ Access Token仍然有效")
            integrator.access_token = credentials["access_token"]
        else:
            print("⚠️ Access Token已过期，正在刷新...")
            if integrator.refresh_access_token():
                integrator.access_token = credentials["access_token"]
    else:
        print("\n需要完成OAuth 2.0授权")
        print("请确保以下信息已配置：")
        print(f"  Client ID: {CLIENT_ID}")
        print(f"  Redirect URI: {REDIRECT_URI}\n")

        # 步骤1：发起授权
        integrator.authorize()

        # 步骤2：获取access token
        try:
            with open("huawei_auth_code.txt", "r") as f:
                auth_code = f.read().strip()

            if integrator.get_access_token(auth_code):
                print("\n✓ 授权成功！")
            else:
                print("\n❌ 授权失败")
                return
        except:
            print("\n❌ 未找到授权码文件")
            return

    # 步骤3：同步数据
    print("\n" + "=" * 60)
    print("开始同步健康数据")
    print("=" * 60)

    data = integrator.sync_data(days=30)

    print("\n" + "=" * 60)
    print("✓ 数据同步完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

## 🔧 配置步骤总结

### API对接所需文件
1. **huawei_healthkit_api.py** - 完整的API对接脚本
2. **huawei_credentials.json** - 存储OAuth凭证（自动生成）
3. **huawei_auth_code.txt** - 临时存储授权码（自动生成）

### 需要在AppGallery Connect获取的信息
- Client ID
- Client Secret
- App ID
- Package Name（如需要）
- SHA256指纹（用于Android应用）

---

## ⚠️ 注意事项

### 审核要求
1. **应用场景说明**：必须详细说明如何使用健康数据
2. **隐私政策**：必须有完整的隐私政策说明数据处理方式
3. **用户授权**：必须明确告知用户哪些数据会被收集
4. **数据安全**：必须说明如何保护用户数据安全

### API限制
1. **调用频率限制**：每分钟最多600次请求
2. **数据量限制**：单次查询最多返回1000条记录
3. **时间范围限制**：单次查询时间跨度不能超过90天
4. **Access Token有效期**：1小时，需要使用refresh_token刷新

### 费用
- 开发者账号：免费
- API调用：免费（需审核通过）
- 企业认证：可能需要费用

---

## 📊 数据对比

| 数据类型 | Oura Ring | 华为Health Kit | 互补性 |
|----------|-----------|----------------|--------|
| HRV | ✓ 详细 | ✓ 基础 | Oura更准确 |
| 睡眠 | ✓ 详细分期 | ✓ 基础分期 | Oura更详细 |
| 心率 | ✓ 采样率低 | ✓ 连续监测 | 华为连续性更好 |
| 血压 | ✗ 不支持 | ✓ 支持 | 华为独有 |
| 潜水 | ✗ 不支持 | ✓ 深度、时长 | 华为独有 |

---

## 🎯 推荐方案

### 对于个人用户（如金明）
**推荐：手动CSV导出**

理由：
- 无需等待1-2周审核
- 无需企业资质
- 立即可用
- 数据完整度80%，足够个人分析

### 对于企业应用
**推荐：Health Kit API**

理由：
- 数据100%完整
- 自动化数据同步
- 可整合到产品中
- 适合为用户提供服务

---

## 📞 下一步行动

### 方式A：手动导出（推荐）
1. 按照上述步骤导出华为健康数据
2. 保存到 `Personal/Health/HuaweiData/HealthData/`
3. 运行整合脚本：
   ```bash
   python3 huawei_oura_integration.py
   ```

### 方式B：申请API接入
1. 确认是否有企业开发者账号
2. 如有，继续按API对接流程操作
3. 如无，建议先使用手动导出，后续再申请企业账号

---

*文档版本：v1.0*
*最后更新：2025-01-31*
*联系方式：通过GitHub Issues反馈问题*
