#!/usr/bin/env python3
"""
看板完整性验证脚本
确保生成的看板文件包含所有必要内容
"""

import sys
from pathlib import Path

def verify_dashboard(md_file_path):
    """验证Markdown看板完整性"""

    print(f"\n🔍 验证看板文件: {md_file_path}")

    required_sections = [
        "📊 今日健康评分",
        "🌤️ 今日天气",
        "🌬️ 空气质量",
        "🎯 训练建议",
        "💡 今日具体推荐",
        "🍽️ 每日饮食建议",
        "🏆 个人最好成绩",
        "💊 补剂提醒"
    ]

    required_keywords = [
        "准备度",
        "睡眠质量",
        "训练类型",
        "小憨眯一下",
        "早餐",
        "训练前加餐",
        "午餐",
        "训练后恢复",
        "晚餐",
        "水分补充",
        "营养时机",
        "补剂清单",
        "应避免的食物"
    ]

    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"\n📊 文件统计:")
        print(f"  文件大小: {len(content)} 字符")
        print(f"  总行数: {content.count(chr(10)) + 1} 行")

        # 检查所有必需章节
        print(f"\n✅ 章节检查:")
        missing_sections = []
        for section in required_sections:
            if section in content:
                print(f"  ✓ {section}")
            else:
                print(f"  ✗ {section} - 缺失!")
                missing_sections.append(section)

        # 检查关键字
        print(f"\n✅ 内容检查:")
        missing_keywords = []
        for keyword in required_keywords:
            if keyword in content:
                print(f"  ✓ {keyword}")
            else:
                print(f"  ✗ {keyword} - 缺失!")
                missing_keywords.append(keyword)

        # 检查重要数据
        print(f"\n✅ 数据检查:")
        checks = {
            "准备度分数": "准备度" in content and "/100" in content,
            "天气数据": "温度" in content and "°C" in content,
            "空气质量": "AQI" in content,
            "睡眠分数": "睡眠质量" in content and "/100" in content,
            "饮食计划": "热量" in content and "kcal" in content,
            "水分补充": "水分" in content and "升" in content
        }

        for check_name, check_result in checks.items():
            if check_result:
                print(f"  ✓ {check_name}")
            else:
                print(f"  ✗ {check_name} - 缺失!")

        # 最终结果
        all_passed = (len(missing_sections) == 0 and
                     len(missing_keywords) == 0 and
                     all(checks.values()))

        if all_passed:
            print(f"\n✅ 看板验证通过！所有内容完整！")
            return True
        else:
            print(f"\n⚠️ 看板验证失败！")
            if missing_sections:
                print(f"  缺失章节: {', '.join(missing_sections)}")
            if missing_keywords:
                print(f"  缺失内容: {', '.join(missing_keywords)}")
            return False

    except FileNotFoundError:
        print(f"\n❌ 错误：文件未找到")
        return False
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        return False


if __name__ == "__main__":
    dashboard_dir = Path.cwd() / "DailyReports"
    today = Path(__file__).stem.split("_")[-1].replace(".py", "")

    # 查找最新的看板文件
    md_files = list(dashboard_dir.glob("dashboard_*.md"))
    if md_files:
        latest_file = max(md_files, key=lambda p: p.stat().st_mtime)
        verify_dashboard(latest_file)
    else:
        print("❌ 未找到看板文件")
        sys.exit(1)
