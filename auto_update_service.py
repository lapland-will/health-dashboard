#!/usr/bin/env python3
"""
金明健康看板 - 自动更新服务
每3小时自动更新看板和图表
"""

import subprocess
import time
import os
from datetime import datetime, timedelta
from pathlib import Path


def update_dashboard():
    """更新看板"""
    try:
        print(f"\n🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动更新看板...")

        # 切换到工作目录
        os.chdir(Path.cwd())

        # 运行主系统
        result = subprocess.run(
            ['python3', 'ultimate_dashboard.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] 看板更新成功！")
            # 统计生成的文件
            reports_dir = Path.cwd() / "DailyReports"
            if reports_dir.exists():
                md_files = list(reports_dir.glob("*.md"))
                html_files = list(reports_dir.glob("*.html"))
                chart_files = list((reports_dir / "charts").glob("*.png")) if (reports_dir / "charts").exists() else []

                print(f"  📄 Markdown文件：{len(md_files)} 个")
                print(f"  🌐 HTML文件：{len(html_files)} 个")
                print(f"  📊 图表文件：{len(chart_files)} 个")
        else:
            print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] 看板目录不存在")

    except subprocess.TimeoutExpired:
        print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] 更新超时（5分钟）")
    except Exception as e:
        print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] 更新失败：{e}")


def auto_update_service():
    """自动更新服务"""
    print("="*60)
    print("🏊 金明健康看板 - 自动更新服务")
    print("="*60)
    print("\n⚙️  配置：")
    print("  • 更新间隔：每3小时")
    print("  • 功能：生成看板、图表、所有HTML版本")
    print("  • 日志：记录每次更新状态")
    print(f"  • 启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 更新内容：")
    print("  • Oura Ring数据")
    print("  • 天气数据")
    print("  • 空气质量数据")
    print("  • 训练建议（泳池训练）")
    print("  • 饮食建议（两餐制）")
    print("  • 补剂清单")
    print("  • 所有图表（8个matplotlib）")
    print("  • 所有HTML看板（4个版本）")
    print("\n🔄 首次更新即将开始...")
    print("="*60 + "\n")

    while True:
        # 立即执行一次更新
        update_dashboard()

        # 计算下次更新时间
        now = datetime.now()
        next_update = now + timedelta(hours=3)

        print(f"\n⏰ 下次更新时间：{next_update.strftime('%H:%M')}")
        print(f"📅 更新日期：{next_update.strftime('%Y-%m-%d')}")
        print(f"⏳ 等待时间：3小时")
        print("="*60 + "\n")

        # 等待3小时
        try:
            # 计算睡眠秒数
            sleep_seconds = 3 * 60 * 60  # 3小时

            # 每分钟打印一次倒计时
            for remaining in range(sleep_seconds, 0, -60):
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                secs = remaining % 60

                if hours > 0:
                    print(f"⏳ 下次更新倒计时：{hours}小时{minutes}分", end='\r')
                elif minutes > 0:
                    print(f"⏳ 下次更新倒计时：{minutes}分{secs}秒", end='\r')
                else:
                    print(f"⏳ 下次更新倒计时：{secs}秒  ", end='\r')

                time.sleep(60)

        except KeyboardInterrupt:
            print("\n\n⚠️ 用户中断，停止自动更新服务")
            break
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            # 继续运行，不退出


def main():
    """主函数"""
    import sys

    print("\n🏊 金明健康看板 - 自动更新服务")
    print("="*60)
    print("\n选择模式：")
    print("1. 立即更新一次")
    print("2. 启动自动更新服务（每3小时）")
    print("0. 退出")

    choice = input("\n请选择（0-2）：").strip()

    if choice == "1":
        update_dashboard()
        print("\n✅ 更新完成！")

    elif choice == "2":
        auto_update_service()

    elif choice == "0":
        print("\n👋 再见！")

    else:
        print("\n⚠️ 无效选择，默认启动自动更新服务...")
        auto_update_service()


if __name__ == "__main__":
    main()
