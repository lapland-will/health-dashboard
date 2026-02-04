#!/usr/bin/env python3
"""
华为运动健康 + Oura Ring 数据整合分析工具
整合过去30天的数据并生成综合报告
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import os

class HuaweiOuraIntegrator:
    """华为和Oura数据整合器"""

    def __init__(self):
        self.base_dir = Path("Personal/Health")
        self.oura_dir = self.base_dir / "OuraDataDaily"
        self.huawei_dir = self.base_dir / "HuaweiData"
        self.integrated_dir = self.base_dir / "IntegratedReports"
        self.integrated_dir.mkdir(parents=True, exist_ok=True)

    def get_oura_last_30_days(self):
        """获取Oura Ring过去30天的数据"""
        print("=" * 60)
        print("读取Oura Ring过去30天数据")
        print("=" * 60)

        oura_data = []

        # 从原始JSON文件读取数据
        data_files = [
            ('readiness', self.base_dir / "OuraData" / "daily_readiness_2026-01-01_to_2026-01-31.json"),
            ('sleep', self.base_dir / "OuraData" / "daily_sleep_2026-01-01_to_2026-01-31.json"),
            ('activity', self.base_dir / "OuraData" / "daily_activity_2026-01-01_to_2026-01-31.json")
        ]

        for data_type, file_path in data_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)

                    # 提取data字段
                    if 'data' in raw_data:
                        daily_records = {}
                        for item in raw_data['data']:
                            date = item.get('day')
                            if date:
                                daily_records[date] = item

                        print(f"  ✓ {data_type}: {len(daily_records)} 天记录")

                        # 创建按日期组织的数据结构
                        for date, record in daily_records.items():
                            # 查找是否已有该日期的数据
                            existing = next((d for d in oura_data if d.get('date') == date), None)
                            if existing:
                                existing[data_type] = record
                            else:
                                new_data = {'date': date, data_type: record}
                                oura_data.append(new_data)

                except Exception as e:
                    print(f"  ⚠ {data_type}: 读取失败 - {e}")
            else:
                print(f"  - {data_type}: 文件不存在")

        # 按日期排序
        oura_data.sort(key=lambda x: x.get('date', ''))

        print(f"\n✓ 共读取 {len(oura_data)} 天的Oura数据")
        return oura_data

    def check_huawei_data(self):
        """检查华为数据是否存在"""
        print("\n" + "=" * 60)
        print("检查华为运动健康数据")
        print("=" * 60)

        # 检查华为数据目录
        huawei_health = self.huawei_dir / "HealthData"
        huawei_dive = self.huawei_dir / "DiveLogs"

        has_health_data = False
        has_dive_data = False

        if huawei_health.exists():
            csv_files = list(huawei_health.glob("*.csv"))
            json_files = list(huawei_health.glob("*.json"))
            if csv_files or json_files:
                has_health_data = True
                print(f"✓ 找到健康数据: {len(csv_files)} 个CSV, {len(json_files)} 个JSON")

        if huawei_dive.exists():
            dive_files = list(huawei_dive.glob("*.*"))
            if dive_files:
                has_dive_data = True
                print(f"✓ 找到潜水数据: {len(dive_files)} 个文件")

        if not has_health_data and not has_dive_data:
            print("⚠ 未找到华为数据")
            print("\n请按以下步骤导出华为运动健康数据：\n")
            print("【方法一：App内导出（推荐）】")
            print("1. 打开华为运动健康App（确保版本≥16.0.12.300）")
            print("2. 进入'健康'页面 → 选择数据类型（如血压）")
            print("3. 点击右上角'导出'图标")
            print("4. 选择时间范围（建议选择过去30天）")
            print("5. 导出为CSV格式")
            print(f"6. 将文件保存到: {huawei_health.absolute()}\n")
            print("【方法二：隐私中心申请副本】")
            print("1. 访问华为隐私中心（网页版）")
            print("2. 登录华为帐号")
            print("3. 选择'获取您的数据副本'")
            print("4. 勾选'运动健康服务'")
            print("5. 等待约7天处理完成")
            print("6. 下载并解压数据")
            print("7. 将数据文件放到上述目录")

        return has_health_data, has_dive_data

    def parse_huawei_data(self):
        """解析华为数据"""
        print("\n" + "=" * 60)
        print("解析华为运动健康数据")
        print("=" * 60)

        huawei_health = self.huawei_dir / "HealthData"
        huawei_data = {}

        # 解析CSV文件
        for csv_file in huawei_health.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                data_type = csv_file.stem
                huawei_data[data_type] = df
                print(f"✓ 已解析: {csv_file.name} ({len(df)} 条记录)")
            except Exception as e:
                print(f"⚠ 解析失败: {csv_file.name} - {e}")

        # 解析JSON文件
        for json_file in huawei_health.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data_type = json_file.stem
                    huawei_data[data_type] = data
                    print(f"✓ 已解析: {json_file.name}")
            except Exception as e:
                print(f"⚠ 解析失败: {json_file.name} - {e}")

        return huawei_data

    def analyze_oura_trends(self, oura_data):
        """分析Oura数据趋势"""
        print("\n" + "=" * 60)
        print("Oura Ring 30天趋势分析")
        print("=" * 60)

        if not oura_data:
            print("无Oura数据可分析")
            return None

        # 提取关键指标
        readiness_scores = []
        sleep_scores = []
        activity_scores = []
        hrv_scores = []

        for day_data in oura_data:
            if day_data.get('readiness'):
                readiness_scores.append(day_data['readiness'].get('score', 0))
                hrv_scores.append(day_data['readiness'].get('contributors', {}).get('hrv_balance', 0))

            if day_data.get('sleep'):
                sleep_scores.append(day_data['sleep'].get('score', 0))

            if day_data.get('activity'):
                activity_scores.append(day_data['activity'].get('score', 0))

        # 计算统计数据
        analysis = {
            "总天数": len(oura_data),
            "准备度": {
                "平均": sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0,
                "最高": max(readiness_scores) if readiness_scores else 0,
                "最低": min(readiness_scores) if readiness_scores else 0
            },
            "睡眠": {
                "平均": sum(sleep_scores) / len(sleep_scores) if sleep_scores else 0,
                "最高": max(sleep_scores) if sleep_scores else 0,
                "最低": min(sleep_scores) if sleep_scores else 0
            },
            "活动": {
                "平均": sum(activity_scores) / len(activity_scores) if activity_scores else 0,
                "最高": max(activity_scores) if activity_scores else 0,
                "最低": min(activity_scores) if activity_scores else 0
            },
            "HRV平衡": {
                "平均": sum(hrv_scores) / len(hrv_scores) if hrv_scores else 0,
                "最高": max(hrv_scores) if hrv_scores else 0,
                "最低": min(hrv_scores) if hrv_scores else 0
            }
        }

        # 打印分析结果
        print(f"\n数据覆盖：{analysis['总天数']} 天")
        print(f"\n准备度分数：")
        print(f"  平均: {analysis['准备度']['平均']:.1f}/100")
        print(f"  范围: {analysis['准备度']['最低']}-{analysis['准备度']['最高']}/100")

        print(f"\n睡眠分数：")
        print(f"  平均: {analysis['睡眠']['平均']:.1f}/100")
        print(f"  范围: {analysis['睡眠']['最低']}-{analysis['睡眠']['最高']}/100")

        print(f"\n活动分数：")
        print(f"  平均: {analysis['活动']['平均']:.1f}/100")
        print(f"  范围: {analysis['活动']['最低']}-{analysis['活动']['最高']}/100")

        print(f"\nHRV平衡：")
        print(f"  平均: {analysis['HRV平衡']['平均']:.1f}/100")
        print(f"  范围: {analysis['HRV平衡']['最低']}-{analysis['HRV平衡']['最高']}/100")

        return analysis

    def generate_integrated_report(self):
        """生成整合的30天报告"""
        print("\n" + "=" * 60)
        print("生成30天综合分析报告")
        print("=" * 60)

        # 获取Oura数据
        oura_data = self.get_oura_last_30_days()

        # 分析Oura数据
        oura_analysis = self.analyze_oura_trends(oura_data)

        # 检查华为数据
        has_health, has_dive = self.check_huawei_data()

        # 解析华为数据（如果存在）
        huawei_data = None
        if has_health or has_dive:
            huawei_data = self.parse_huawei_data()

        # 生成报告
        report = {
            "报告生成时间": datetime.now().isoformat(),
            "用户": "金明 - 自由潜水世界纪录保持者",
            "数据期间": f"过去30天 ({(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')} 至 {datetime.now().strftime('%Y-%m-%d')})",
            "数据来源": ["Oura Ring Gen 3"],
            "Oura Ring分析": oura_analysis,
            "华为WATCH Ultimate 2": {
                "状态": "已连接但数据未导出" if not (has_health or has_dive) else "数据已导出并解析",
                "健康数据": has_health,
                "潜水数据": has_dive
            }
        }

        # 保存报告
        report_file = self.integrated_dir / f"integrated_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 生成Markdown报告
        self._generate_markdown_report(report, oura_data, huawei_data)

        print(f"\n✓ 报告已保存: {report_file}")
        print(f"✓ Markdown报告已保存: {self.integrated_dir / '30_day_report.md'}")

    def _generate_markdown_report(self, report, oura_data, huawei_data):
        """生成Markdown格式的报告"""
        md_content = f"""# 金明 - 30天健康数据综合报告

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**数据期间：** 过去30天
**用户：** 自由潜水世界纪录保持者

---

## 📊 数据概览

### 数据来源
- ✓ Oura Ring Gen 3: {report['Oura Ring分析']['总天数']}天数据
- {"✓" if report['华为WATCH Ultimate 2']['健康数据'] else "○"} 华为WATCH Ultimate 2: {report['华为WATCH Ultimate 2']['状态']}

---

## Oura Ring 30天趋势分析

### 整体状况

| 指标 | 平均 | 范围 | 评价 |
|------|------|------|------|
| **准备度分数** | {report['Oura Ring分析']['准备度']['平均']:.1f}/100 | {report['Oura Ring分析']['准备度']['最低']}-{report['Oura Ring分析']['准备度']['最高']}/100 | {"优秀" if report['Oura Ring分析']['准备度']['平均'] >= 85 else "良好" if report['Oura Ring分析']['准备度']['平均'] >= 70 else "需关注"} |
| **睡眠分数** | {report['Oura Ring分析']['睡眠']['平均']:.1f}/100 | {report['Oura Ring分析']['睡眠']['最低']}-{report['Oura Ring分析']['睡眠']['最高']}/100 | {"优秀" if report['Oura Ring分析']['睡眠']['平均'] >= 85 else "良好"} |
| **活动分数** | {report['Oura Ring分析']['活动']['平均']:.1f}/100 | {report['Oura Ring分析']['活动']['最低']}-{report['Oura Ring分析']['活动']['最高']}/100 | {"优秀" if report['Oura Ring分析']['活动']['平均'] >= 85 else "良好"} |
| **HRV平衡** | {report['Oura Ring分析']['HRV平衡']['平均']:.1f}/100 | {report['Oura Ring分析']['HRV平衡']['最低']}-{report['Oura Ring分析']['HRV平衡']['最高']}/100 | {"优秀" if report['Oura Ring分析']['HRV平衡']['平均'] >= 85 else "良好"} |

### 趋势分析

"""

        # 添加最近7天的详细数据
        if oura_data:
            md_content += "\n### 最近7天详细数据\n\n"
            md_content += "| 日期 | 准备度 | 睡眠 | 活动 | HRV平衡 |\n"
            md_content += "|------|--------|------|------|----------|\n"

            for day_data in oura_data[-7:]:
                date = day_data.get('date', 'N/A')
                readiness = day_data.get('readiness', {}).get('score', 'N/A')
                sleep = day_data.get('sleep', {}).get('score', 'N/A')
                activity = day_data.get('activity', {}).get('score', 'N/A')
                hrv = day_data.get('readiness', {}).get('contributors', {}).get('hrv_balance', 'N/A')

                md_content += f"| {date} | {readiness} | {sleep} | {activity} | {hrrv} |\n"

        # 添加华为数据部分（如果有）
        if huawei_data:
            md_content += "\n---\n\n## 华为WATCH Ultimate 2 数据\n\n"
            for data_type, data in huawei_data.items():
                if isinstance(data, pd.DataFrame):
                    md_content += f"\n### {data_type}\n"
                    md_content += f"- 记录数: {len(data)}\n"
                    md_content += f"- 字段: {list(data.columns)}\n"
                elif isinstance(data, dict):
                    md_content += f"\n### {data_type}\n"
                    md_content += f"- 数据键: {list(data.keys())}\n"

        # 添加建议
        avg_readiness = report['Oura Ring分析']['准备度']['平均']
        avg_hrv = report['Oura Ring分析']['HRV平衡']['平均']

        md_content += f"""

---

## 自由潜水训练建议

### 当前状态评估

**准备度：{avg_readiness:.1f}/100** {"✓ 优秀" if avg_readiness >= 85 else "✓ 良好" if avg_readiness >= 70 else "⚠️ 需关注"}

**HRV平衡：{avg_hrv:.1f}/100** {"✓ 良好" if avg_hrv >= 85 else "✓ 可接受" if avg_hrv >= 70 else "⚠️ 需关注"}

### 训练建议

"""

        if avg_readiness >= 85:
            md_content += "- ✓ 可以进行高强度闭气训练\n"
            md_content += "- ✓ 适合深度挑战\n"
        elif avg_readiness >= 70:
            md_content += "- ✓ 适合中等强度训练\n"
            md_content += "- ⚠️ 注意训练强度\n"
        else:
            md_content += "- ⚠️ 建议休息或轻度训练\n"
            md_content += "- ⚠️ 优先恢复\n"

        md_content += f"""

### 恢复建议

- HRV平衡: {avg_hrv:.1f}/100 - {'自主神经系统恢复良好，适合训练' if avg_hrv >= 85 else '建议注意训练强度和恢复时间' if avg_hrv >= 70 else '可能存在疲劳，建议减少训练强度'}
- 建议充分休息，保证7-9小时睡眠

---

## 数据文件位置

- **JSON报告**: `{self.integrated_dir.relative_to(self.base_dir)}/integrated_report_{datetime.now().strftime('%Y%m%d')}.json`
- **Markdown报告**: `{self.integrated_dir.relative_to(self.base_dir)}/30_day_report.md`
- **Oura原始数据**: `{self.oura_dir.relative_to(self.base_dir)}/`
- **华为数据**: `{self.huawei_dir.relative_to(self.base_dir)}/`

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

        md_file = self.integrated_dir / "30_day_report.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

def main():
    """主函数"""
    integrator = HuaweiOuraIntegrator()

    print("华为运动健康 + Oura Ring 数据整合工具")
    print("=" * 60)

    # 生成整合报告
    integrator.generate_integrated_report()

    print("\n" + "=" * 60)
    print("✓ 数据整合完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
