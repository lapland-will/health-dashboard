#!/usr/bin/env python3
"""
华为运动健康数据解析器
用于分析导出的CSV文件并整合到健康记录系统
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

class HuaweiHealthParser:
    """华为运动健康数据解析器"""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = Path("Personal/Health/HuaweiData")
        self.data_dir = Path(data_dir)
        self.health_dir = self.data_dir / "HealthData"
        self.dive_dir = self.data_dir / "DiveLogs"
        self.workout_dir = self.data_dir / "Workouts"

        # 创建目录
        for d in [self.data_dir, self.health_dir, self.dive_dir, self.workout_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def parse_blood_pressure_csv(self, csv_file):
        """
        解析血压数据CSV
        :param csv_file: CSV文件路径
        :return: DataFrame
        """
        try:
            df = pd.read_csv(csv_file)

            print("=" * 60)
            print("血压数据分析")
            print("=" * 60)
            print(f"\n记录总数：{len(df)}")

            # 尝试识别常见列名
            date_col = self._find_column(df, ['日期', 'date', '时间', 'time'])
            sys_col = self._find_column(df, ['收缩压', 'systolic', '高压'])
            dia_col = self._find_column(df, ['舒张压', 'diastolic', '低压'])
            hr_col = self._find_column(df, ['心率', 'heart rate', 'pulse'])

            if date_col and sys_col:
                print(f"\n时间范围：{df[date_col].iloc[0]} 至 {df[date_col].iloc[-1]}")
                print(f"平均收缩压：{df[sys_col].mean():.1f} mmHg")

                if dia_col:
                    print(f"平均舒张压：{df[dia_col].mean():.1f} mmHg")

                if hr_col:
                    print(f"平均心率：{df[hr_col].mean():.1f} bpm")

                # 保存分析结果
                summary = {
                    "解析时间": datetime.now().isoformat(),
                    "记录数": int(len(df)),
                    "平均收缩压": float(df[sys_col].mean()),
                    "平均舒张压": float(df[dia_col].mean()) if dia_col else None,
                    "平均心率": float(df[hr_col].mean()) if hr_col else None
                }

                summary_file = self.health_dir / "blood_pressure_summary.json"
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)

                print(f"\n✓ 分析结果已保存: {summary_file}")

            return df

        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return None

    def _find_column(self, df, possible_names):
        """查找可能的列名"""
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    def parse_dive_log(self, log_file):
        """
        解析潜水日志
        :param log_file: 日志文件路径（CSV或JSON）
        """
        try:
            if log_file.suffix == '.csv':
                df = pd.read_csv(log_file)
                self._analyze_dive_data(df)
            elif log_file.suffix == '.json':
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._analyze_dive_data(data)

        except Exception as e:
            print(f"❌ 解析潜水日志失败: {e}")

    def _analyze_dive_data(self, data):
        """分析潜水数据"""
        print("\n" + "=" * 60)
        print("潜水数据分析")
        print("=" * 60)

        # 这里根据实际数据格式进行解析
        # TODO: 实现具体的潜水数据分析逻辑

        print("\n潜水数据分析功能开发中...")
        print("请确保导出的数据包含以下信息：")
        print("- 潜水日期和时间")
        print("- 最大深度")
        print("- 下潜时间")
        print("- 水面休息时间")
        print("- 温度数据")

    def integrate_with_oura(self, oura_data_dir):
        """
        与Oura Ring数据整合
        :param oura_data_dir: Oura数据目录
        """
        oura_dir = Path(oura_data_dir)

        if not oura_dir.exists():
            print(f"❌ Oura数据目录不存在: {oura_dir}")
            return

        print("\n" + "=" * 60)
        print("整合Oura Ring数据")
        print("=" * 60)

        # 读取最新的Oura数据
        oura_daily = oura_dir / "OuraDataDaily"

        if oura_daily.exists():
            # 获取最近7天的数据
            recent_days = sorted(oura_daily.iterdir())[-7:]

            print(f"\n找到 {len(recent_days)} 天的Oura数据")

            for day_dir in recent_days:
                summary_file = day_dir / "daily_summary.json"
                if summary_file.exists():
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        date = data.get('date')
                        readiness = data.get('readiness', {}).get('score') if data.get('readiness') else None
                        sleep_score = data.get('sleep', {}).get('score') if data.get('sleep') else None

                        print(f"  {date}: 准备度={readiness}, 睡眠={sleep_score}")
        else:
            print("未找到Oura Ring数据")

    def generate_integrated_report(self):
        """生成整合分析报告"""
        print("\n" + "=" * 60)
        print("生成整合分析报告")
        print("=" * 60)

        report = {
            "生成时间": datetime.now().isoformat(),
            "用户": "金明 - 自由潜水运动员",
            "数据源": ["华为WATCH Ultimate 2", "Oura Ring Gen 3"],
            "状态": "数据收集中"
        }

        report_file = self.data_dir / "integrated_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n✓ 整合报告已保存: {report_file}")

def main():
    """主函数"""
    parser = HuaweiHealthParser()

    print("华为运动健康数据解析器")
    print("=" * 60)

    # 检查是否有数据文件
    csv_files = list(parser.health_dir.glob("*.csv"))

    if csv_files:
        print(f"\n找到 {len(csv_files)} 个数据文件")
        for csv_file in csv_files:
            print(f"\n处理文件: {csv_file.name}")
            parser.parse_blood_pressure_csv(csv_file)
    else:
        print("\n未找到健康数据文件")
        print("\n请按以下步骤导出华为运动健康数据：")
        print("\n【血压数据导出】")
        print("1. 打开华为运动健康App（确保版本≥16.0.12.300）")
        print("2. 进入'健康'页面")
        print("3. 点击'血压'卡片")
        print("4. 点击右上角'更多'或'导出'")
        print("5. 选择时间范围")
        print("6. 导出为CSV格式")
        print("7. 保存到以下目录：")
        print(f"   {parser.health_dir.absolute()}")

        print("\n【其他数据导出】")
        print("1. 打开华为运动健康App")
        print("2. 进入'我的' → 点击个人头像")
        print("3. 进入'账号中心'")
        print("4. 选择'请求副本数据'")
        print("5. 等待邮件通知（约7天）")

    print("\n" + "=" * 60)
    print("提示：")
    print("- 支持的数据格式：CSV、JSON")
    print("- 数据将自动整合到健康记录系统")
    print("- 与Oura Ring数据对比分析功能开发中")
    print("=" * 60)

if __name__ == "__main__":
    main()
