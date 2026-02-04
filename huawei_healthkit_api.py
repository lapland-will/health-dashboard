#!/usr/bin/env python3
"""
华为Health Kit API完整对接脚本
包含OAuth 2.0认证和数据获取功能

使用前准备：
1. 在华为AppGallery Connect创建项目
2. 开通Health Kit服务
3. 获取Client ID和Client Secret
4. 配置OAuth 2.0重定向URI

作者：健康数据整合系统
更新：2025-01-31
"""

import requests
import json
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time

# ==================== 配置区域 ====================
# 请在AppGallery Connect获取以下信息

CLIENT_ID = "your_client_id_here"  # 替换为你的Client ID
CLIENT_SECRET = "your_client_secret_here"  # 替换为你的Client Secret
REDIRECT_URI = "http://localhost:8000/callback"

# OAuth权限范围
SCOPE = "openid https://www.huawei.com/healthkit/healthdata.read"

# API端点
AUTH_URL = "https://oauth-login.cloud.huawei.com/oauth2/v3/authorize"
TOKEN_URL = "https://oauth-login.cloud.huawei.com/oauth2/v3/token"
API_BASE_URL = "https://health.huawei.com/cloud/hhi/api"

# =================================================


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """处理OAuth 2.0回调请求"""

    def log_message(self, format, *args):
        """禁用默认日志输出"""
        pass

    def do_GET(self):
        if self.path.startswith("/callback"):
            # 解析URL参数
            try:
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = {}
                for param in query.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        params[key] = value

                auth_code = params.get("code")
                error = params.get("error")

                # 返回响应页面
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()

                if auth_code:
                    # 保存授权码
                    with open("huawei_auth_code.txt", "w") as f:
                        f.write(auth_code)

                    html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <title>授权成功</title>
                        <style>
                            body {
                                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            }
                            .container {
                                background: white;
                                padding: 40px;
                                border-radius: 10px;
                                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                                text-align: center;
                            }
                            h1 { color: #10b981; margin-bottom: 20px; }
                            p { color: #666; font-size: 16px; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>✓ 授权成功！</h1>
                            <p>您可以关闭此窗口，返回终端查看结果</p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode('utf-8'))
                    print(f"\n✓ 收到授权码: {auth_code[:20]}...")

                elif error:
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <title>授权失败</title>
                    </head>
                    <body>
                        <h1>❌ 授权失败</h1>
                        <p>错误: {error}</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode('utf-8'))
                    print(f"\n❌ 授权被拒绝: {error}")
                else:
                    print("\n⚠️ 未收到授权码")

            except Exception as e:
                print(f"\n❌ 处理回调时出错: {e}")


class HuaweiHealthKitAPI:
    """华为Health Kit API客户端"""

    def __init__(self, client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.credentials_file = Path("huawei_credentials.json")
        self.base_dir = Path.cwd() / "Personal" / "Health" / "HuaweiData"
        self.health_data_dir = self.base_dir / "HealthData"
        self.health_data_dir.mkdir(parents=True, exist_ok=True)

    def _encode_params(self, params):
        """编码URL参数"""
        return "&".join([f"{k}={v}" for k, v in params.items()])

    def load_credentials(self):
        """从文件加载凭证"""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    credentials = json.load(f)
                    self.access_token = credentials.get("access_token")
                    self.refresh_token = credentials.get("refresh_token")
                    self.expires_at = datetime.fromisoformat(
                        credentials.get("expires_at")
                    ) if credentials.get("expires_at") else None
                return True
            except Exception as e:
                print(f"⚠️ 加载凭证失败: {e}")
        return False

    def save_credentials(self):
        """保存凭证到文件"""
        credentials = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "updated_at": datetime.now().isoformat()
        }

        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f, indent=2, ensure_ascii=False)

        print(f"✓ 凭证已保存到 {self.credentials_file}")

    def authorize(self):
        """步骤1：发起OAuth 2.0授权"""
        state = secrets.token_urlsafe(16)

        auth_params = {
            "client_id": self.client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "state": state
        }

        auth_url = f"{AUTH_URL}?{self._encode_params(auth_params)}"

        print("\n" + "=" * 60)
        print("华为Health Kit OAuth 2.0 授权")
        print("=" * 60)
        print("\n请在浏览器中完成授权：")
        print(f"\n{auth_url}\n")
        print("等待授权回调...\n")

        # 启动本地服务器并打开浏览器
        server = HTTPServer(("localhost", 8000), OAuthCallbackHandler)
        server.timeout = 300  # 5分钟超时

        # 在新线程中打开浏览器
        def open_browser():
            time.sleep(1)
            webbrowser.open(auth_url)

        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        # 处理请求
        server.handle_request()

        # 检查是否收到授权码
        auth_code_file = Path("huawei_auth_code.txt")
        if auth_code_file.exists():
            with open(auth_code_file, 'r') as f:
                auth_code = f.read().strip()

            # 删除临时文件
            auth_code_file.unlink()

            return auth_code

        return None

    def get_access_token(self, auth_code):
        """步骤2：使用授权码获取access token"""
        print("\n正在获取Access Token...")

        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": REDIRECT_URI
        }

        try:
            response = requests.post(TOKEN_URL, data=data)
            result = response.json()

            if "access_token" in result:
                self.access_token = result["access_token"]
                self.refresh_token = result.get("refresh_token")
                self.expires_at = datetime.now() + timedelta(hours=1)  # Token有效期1小时

                self.save_credentials()

                print("✓ Access Token获取成功")
                print(f"✓ 有效期至: {self.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")

                return True
            else:
                print("❌ 获取Access Token失败：")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return False

        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False

    def refresh_access_token(self):
        """刷新access token"""
        if not self.refresh_token:
            print("❌ 没有refresh_token，需要重新授权")
            return False

        print("\n正在刷新Access Token...")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(TOKEN_URL, data=data)
            result = response.json()

            if "access_token" in result:
                self.access_token = result["access_token"]
                if "refresh_token" in result:
                    self.refresh_token = result["refresh_token"]
                self.expires_at = datetime.now() + timedelta(hours=1)

                self.save_credentials()

                print("✓ Access Token刷新成功")
                return True
            else:
                print("❌ 刷新失败：")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return False

        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False

    def ensure_valid_token(self):
        """确保有有效的access token"""
        # 尝试从文件加载
        if not self.access_token:
            self.load_credentials()

        # 检查是否过期
        if self.access_token and self.expires_at:
            if datetime.now() >= self.expires_at:
                print("⚠️ Access Token已过期")
                return self.refresh_access_token()
            return True

        # 没有token，需要授权
        return False

    def _make_api_request(self, endpoint, payload):
        """发起API请求"""
        if not self.ensure_valid_token():
            print("❌ 无有效的Access Token")
            return None

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{API_BASE_URL}/{endpoint}",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("⚠️ Token可能已失效，尝试刷新...")
                if self.refresh_access_token():
                    # 重试请求
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    response = requests.post(
                        f"{API_BASE_URL}/{endpoint}",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    if response.status_code == 200:
                        return response.json()

            print(f"❌ API请求失败 (HTTP {response.status_code})")
            print(response.text)
            return None

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None

    def get_health_data(self, data_type, start_date, end_date):
        """
        获取健康数据
        :param data_type: 数据类型代码（如 HEALTH_CP_HEART_RATE）
        :param start_date: 开始日期 (datetime对象)
        :param end_date: 结束日期 (datetime对象)
        """
        payload = {
            "dataType": data_type,
            "startTime": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endTime": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pageIndex": 1,
            "pageSize": 1000
        }

        return self._make_api_request("healthdata/data/query", payload)

    def sync_blood_pressure(self, days=30):
        """同步血压数据"""
        print(f"\n同步血压数据（过去{days}天）...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        data = self.get_health_data(
            "HEALTH_CP_BLOOD_PRESSURE",
            start_date,
            end_date
        )

        if data:
            output_file = self.health_data_dir / f"blood_pressure_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ 血压数据已保存: {output_file}")
            return data

        return None

    def sync_heart_rate(self, days=30):
        """同步心率数据"""
        print(f"\n同步心率数据（过去{days}天）...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        data = self.get_health_data(
            "HEALTH_CP_HEART_RATE",
            start_date,
            end_date
        )

        if data:
            output_file = self.health_data_dir / f"heart_rate_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ 心率数据已保存: {output_file}")
            return data

        return None

    def sync_sleep_data(self, days=30):
        """同步睡眠数据"""
        print(f"\n同步睡眠数据（过去{days}天）...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        data = self.get_health_data(
            "HEALTH_CP_SLEEP",
            start_date,
            end_date
        )

        if data:
            output_file = self.health_data_dir / f"sleep_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ 睡眠数据已保存: {output_file}")
            return data

        return None

    def sync_step_count(self, days=30):
        """同步步数数据"""
        print(f"\n同步步数数据（过去{days}天）...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        data = self.get_health_data(
            "HEALTH_CP_STEP_COUNT",
            start_date,
            end_date
        )

        if data:
            output_file = self.health_data_dir / f"step_count_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ 步数数据已保存: {output_file}")
            return data

        return None

    def sync_all_data(self, days=30):
        """同步所有健康数据"""
        print("\n" + "=" * 60)
        print(f"开始同步华为健康数据（过去{days}天）")
        print("=" * 60)

        results = {
            "blood_pressure": self.sync_blood_pressure(days),
            "heart_rate": self.sync_heart_rate(days),
            "sleep": self.sync_sleep_data(days),
            "step_count": self.sync_step_count(days)
        }

        # 生成汇总报告
        summary = {
            "sync_time": datetime.now().isoformat(),
            "data_period_days": days,
            "start_date": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "results": {k: v is not None for k, v in results.items()}
        }

        summary_file = self.health_data_dir / "sync_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 60)
        print("数据同步完成")
        print("=" * 60)
        print(f"\n汇总：")
        for data_type, success in summary["results"].items():
            status = "✓ 成功" if success else "❌ 失败"
            print(f"  {data_type}: {status}")

        return results


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("华为Health Kit API 对接工具")
    print("=" * 60)

    # 检查配置
    if CLIENT_ID == "your_client_id_here":
        print("\n❌ 请先配置Client ID和Client Secret")
        print("\n步骤：")
        print("1. 访问 https://developer.huawei.com/")
        print("2. 注册企业开发者账号")
        print("3. 在AppGallery Connect创建应用")
        print("4. 开通Health Kit服务")
        print("5. 获取Client ID和Client Secret")
        print("6. 编辑此文件，填入CLIENT_ID和CLIENT_SECRET")
        print("\n详细步骤请参考: HuaweiHealthKitAPI对接指南.md")
        return

    # 创建API客户端
    api = HuaweiHealthKitAPI()

    # 尝试加载已有凭证
    if api.load_credentials():
        if api.expires_at and datetime.now() < api.expires_at:
            print(f"\n✓ 发现有效凭证 (有效期至: {api.expires_at.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print("\n⚠️ 发现凭证但已过期，尝试刷新...")
            if not api.refresh_access_token():
                print("\n需要重新授权")
            else:
                print("✓ 凭证已刷新")

    # 如果没有有效凭证，进行授权
    if not api.access_token:
        print("\n未找到有效凭证，需要进行OAuth 2.0授权")
        auth_code = api.authorize()

        if auth_code:
            if api.get_access_token(auth_code):
                print("\n✓ 授权成功！")
            else:
                print("\n❌ 授权失败")
                return
        else:
            print("\n❌ 未收到授权码")
            return

    # 同步数据
    results = api.sync_all_data(days=30)

    print("\n✓ 所有操作完成！")
    print(f"\n数据保存位置: {api.health_data_dir.absolute()}")


if __name__ == "__main__":
    main()
