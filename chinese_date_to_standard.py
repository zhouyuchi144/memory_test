from datetime import datetime, timedelta
import re

def get_valid_time(year, month, day, time_part):
    try:
        date_part = datetime(year, month, day)
        combined = datetime.combine(date_part.date(), time_part)
        return combined.strftime("%Y-%m-%d")
    except:
        return "invalid_date"

def get_valid_time2(current, delta, time_part):
    try:
        date_part = current + timedelta(days=delta)
        combined = datetime.combine(date_part.date(), time_part)
        return combined.strftime("%Y-%m-%d")
    except:
        return "invalid_date"

def chinese_date_to_standard(start_date_chinese, start_time, current_time):
    current = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    time_part = datetime.strptime(start_time, "%H:%M:%S").time()
    
    # 绝对日期：2025年7月8日格式
    match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', start_date_chinese)
    if match:
        year, month, day = map(int, match.groups())
        return get_valid_time(year, month, day, time_part)
    
    # 7月8日格式
    match = re.match(r"(\d{1,2})月(\d{1,2})[日号]", start_date_chinese)
    if match:
        month, day = map(int, match.groups())
        year = current.year
        if month < current.month or (month == current.month and day < current.day):
            year += 1
        return get_valid_time(year, month, day, time_part)
    
    # 每月5号格式
    match = re.match(r'每个?月(\d{1,2})号', start_date_chinese)
    if match:
        day = int(match.group(1))
        day_curr = current.day
        year = current.year
        month = current.month if day >= day_curr else current.month + 1
        if month > 12:
            month = 1
            year += 1
        return get_valid_time(year, month, day, time_part)
    
    # 下个月5号格式
    match = re.match(r'下个?月(\d{1,2})号', start_date_chinese)
    if match:
        day = int(match.group(1))
        month = current.month + 1
        year = current.year
        if month > 12:
            month = 1
            year += 1
        return get_valid_time(year, month, day, time_part)

    # 相对日期：周X/下周X格式
    match = re.match(r'(下{0,6})[周|礼拜|星期]([一二三四五六日天1234567])', start_date_chinese)
    if match:
        weekday_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7, '天': 7, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7}
        next_cnt = len(match.group(1))
        weekday_target = weekday_map.get(match.group(2))
        weekday_current = current.weekday() + 1
        delta = (weekday_target - weekday_current) % 7 if next_cnt == 0 else (weekday_target - weekday_current) + 7 * next_cnt
        return get_valid_time2(current, delta, time_part)

    # 相对日期：今天/明天/后天
    match = re.match(r'([今明后])[天早晚]?', start_date_chinese)
    if match:
        delta_map = {'今': 0, '明': 1, '后': 2}
        delta = delta_map.get(match.group(1))
        return get_valid_time2(current, delta, time_part)
    
    return None  # 无法解析的格式


# 测试用例
if __name__ == "__main__":
    test_cases = [
        ("2025-07-03 10:00:00", "今晚", "15:00:00", "2025-07-03"),
        ("2025-07-03 10:00:00", "明早", "15:00:00", "2025-07-04"),
        ("2025-07-03 10:00:00", "后天", "15:00:00", "2025-07-05"),
        ("2025-07-03 10:00:00", "周三", "15:00:00", "2025-07-09"),
        ("2025-07-03 16:00:00", "周四", "15:00:00", "2025-07-03"),  # 本周四已过，也返回本周四（后面会有判断过期的逻辑）
        ("2025-07-03 10:00:00", "周四", "15:00:00", "2025-07-03"),  # 本周四尚未过
        ("2025-07-03 10:00:00", "下周一", "15:00:00", "2025-07-07"),
        ("2025-07-03 10:00:00", "下周日", "15:00:00", "2025-07-13"),
        ("2025-07-03 10:00:00", "下下周日", "15:00:00", "2025-07-20"),
        ("2025-02-28 10:00:00", "下个月5号", "10:00:00", "2025-03-05"),
        ("2025-12-31 10:00:00", "下个月5号", "10:00:00", "2026-01-05"),  # 跨年
        ("2025-07-03 10:00:00", "7月8日", "15:00:00", "2025-07-08"),
        ("2025-12-03 10:00:00", "7月8日早8点", "15:00:00", "2026-07-08"),  # 跨年
        ("2025-07-03 10:00:00", "2026年7月8日", "15:00:00", "2026-07-08"),
        ("2025-07-03 10:00:00", "每个月5号", "15:00:00", "2025-07-05"),
        ("2025-07-03 10:00:00", "每月5号", "15:00:00", "2025-07-05"),
        ("2025-07-05 16:00:00", "每月5号", "15:00:00", "2025-07-05"),  # 今日的情况：本月x号已过，也返回今天
        ("2025-02-18 10:00:00", "每月30号", "10:00:00", "invalid_date"),  # 无效日期处理
    ]

    for current_time, chinese_date, start_time, expected in test_cases:
        result = chinese_date_to_standard(chinese_date, start_time, current_time)
        print(f"输入: 日期: '{chinese_date}', 时间: {start_time}, 当前时间: {current_time}")
        print(f"输出: {result} {'✓' if result == expected else '✗ (应为: ' + expected + ')'}")
        print()
