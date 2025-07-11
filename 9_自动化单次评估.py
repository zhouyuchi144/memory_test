import random
import pandas as pd
import json
import re
from datetime import datetime, timedelta



keys = ['memory_type', 'memory_subtype', 'content', 'place', 'related_person', 'start_time', 'end_time', 'remind_time',
        'is_repeat_time', 'repeat_freq', 'repeat_value', 'repeat_last_time'
        , 'start_time_chinese', 'end_time_chinese', 'remind_time_chinese'
       ]

# keys = ['memory_type', 'memory_subtype', 'content', 'place', 'related_person', 'start_time_has_hour', 'start_time', 'end_time', 'remind_time']


num_map = {'半': 0.5, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15, '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
           '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25, '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30, '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34,'三十五': 35, '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40,
           '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44, '四十五': 45, '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50, '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54, '五十五': 55, '五十六': 56, '五十七': 57, '五十八': 58, '五十九': 59, '六十': 60}
def chinese_to_num(value):
    return num_map.get(value) if num_map.get(value) else int(value)

def time_add_minute(time_str, delta):
    if not time_str: return ''
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    new_dt = dt + timedelta(minutes=delta)
    return new_dt.strftime("%Y-%m-%d %H:%M:%S")

def str2json_llm_output(arg1):
    if not arg1: return {}
    try:
        if isinstance(arg1, str):
            pattern = re.compile(r'```(json)?\n?|```\n?')
            r = pattern.sub('', arg1)
            return json.loads(r)
        else:
            return arg1
    except:
        return {}

def exchange_remind_time(remind_time, current_time):
    dt1 = datetime.strptime(current_time[0:10], "%Y-%m-%d")
    dt2 = datetime.strptime(remind_time[0:10], "%Y-%m-%d")
    delta = (dt2-dt1).days

    dt0 = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    dt = datetime.strptime(remind_time, "%Y-%m-%d %H:%M:%S")
    weekday0 = dt0.weekday()
    weekday = dt.weekday()  #获取周几（0=周一，6=周日）
    weekday_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday]
    month = dt.month
    day = dt.day
    reply_day = f"{month}月{day}号"
    if delta < 0:
        return [f"这{weekday_name}{remind_time[11:16]}"]
    elif delta == 0:
        r = [f"这{weekday_name}{remind_time[11:16]}", f"{weekday_name}{remind_time[11:16]}"]
        if weekday_name == '周日': r.extend([f"这周天{remind_time[11:16]}", f"周天{remind_time[11:16]}"])
    elif delta <= (7+6-weekday0):
        if delta >= 7:
            r = [f"下{weekday_name}{remind_time[11:16]}"]
            if weekday_name == '周日': r.extend([f"下周天{remind_time[11:16]}"])
        elif weekday0 > weekday:
            r = [f"{weekday_name}{remind_time[11:16]}", f"下{weekday_name}{remind_time[11:16]}"]
            if weekday_name == '周日': r.extend([f"周天{remind_time[11:16]}", f"下周天{remind_time[11:16]}"])
        else:
            r = [f"这{weekday_name}{remind_time[11:16]}", f"{weekday_name}{remind_time[11:16]}"]
            if weekday_name == '周日': r.extend([f"这周天{remind_time[11:16]}", f"周天{remind_time[11:16]}"])
    else:
        r = [f"{reply_day}{remind_time[11:16]}"]
    if delta == 0:
        r.append(f"今天{remind_time[11:16]}")
    elif delta == 1:
        r.append(f"明天{remind_time[11:16]}")
    elif delta == 2:
        r.append(f"后天{remind_time[11:16]}")
    return r


def get_time_value(value):
    if not value: return ''
    if len(value) == 19:
        return '`'+value
    else:
        return '`'+f"{value[:4]}-{value[4:6]}-{value[6:]}"
def get_start_time_has_hour(d):
    if d.get('start_time_is_accurate'):
        start_time_has_hour = d.get('start_time_is_accurate', '')
    elif d.get('start_time_has_hour') == '是' and str(d.get('start_time_not_right')) == '0':
        start_time_has_hour = '是'
    else:
        start_time_has_hour = '否'
    return start_time_has_hour

def get_answer_from_file_json(df):
    answer = []
    df['result'] = df['生成结果'].apply(lambda x: str2json_llm_output(json.loads(x)['result']))
    for i, row in df.iterrows():
        d = row['result']
        v = {}
        start_time_has_hour = get_start_time_has_hour(d)
        for key in keys+['current_time', 'query_hist']:
            if key in ('start_time', 'end_time', 'remind_time'):
                v[key] = get_time_value(d.get(key))
                # if start_time_has_hour == '是':
                #     v[key] = get_time_value(d.get(key))
                # else:
                #     v[key] = ''
            elif key == 'start_time_has_hour':
                v[key] = start_time_has_hour
            else:
                v[key] = str(d.get(key, ''))
        answer.append(v)
    return answer

def get_answer_from_file(file):
    df = pd.read_csv(file)
    if df.shape[1] <= 3: return get_answer_from_file_json(df)
    answer = []
    for i, row in df.iterrows():
        v = {}
        for key in keys+['current_time', 'query_hist']:
            value = str(row[key])
            value = '' if value == 'nan' else value
            if key in ('start_time', 'end_time', 'remind_time'):
                v[key] = value if value else ''
                # # if row['start_time_has_hour'] == '是' and str(row['start_time_not_right']) == '0':
                # if row['start_time_has_hour'] == '是':
                #     v[key] = value if value else ''
                # else:
                #     v[key] = ''
            else:
                v[key] = value
        answer.append(v)
    return answer

def exchange_time_match0(match):
    m1 = match.group(1) if match.group(1) else ''
    if m1 and m1 in ('今', '明', '后'): m1 = f"{m1}天"
    if m1 and m1 in ('今日', '明日', '后日'): m1 = f"{m1[0]}天"
    hour = chinese_to_num(match.group(3))
    if match.group(2) and match.group(2) in ('下午', '晚上', '夜里', '晚') and hour < 12: hour += 12
    if match.group(2) and match.group(2) in ('中午') and hour < 8: hour += 12
    minute = chinese_to_num(match.group(4))
    # print(match.groups(), f"{m1}{(hour):02d}:{(minute):02d}")
    return f"{m1}{(hour):02d}:{(minute):02d}"
def exchange_time_match1(match):
    m1 = match.group(1) if match.group(1) else ''
    if m1 and m1 in ('今', '明', '后'): m1 = f"{m1}天"
    if m1 and m1 in ('今日', '明日', '后日'): m1 = f"{m1[0]}天"
    hour = chinese_to_num(match.group(3))
    if match.group(2) and match.group(2) in ('下午', '晚上', '夜里', '晚') and hour < 12: hour += 12
    if match.group(2) and match.group(2) in ('中午') and hour < 8: hour += 12
    # print(match.groups(), f"{m1}{(hour):02d}:30")
    return f"{m1}{(hour):02d}:30"
def exchange_time_match2(match):
    m1 = match.group(1) if match.group(1) else ''
    if m1 and m1 in ('今', '明', '后'): m1 = f"{m1}天"
    if m1 and m1 in ('今日', '明日', '后日'): m1 = f"{m1[0]}天"
    hour = chinese_to_num(match.group(3))
    if match.group(2) and match.group(2) in ('下午', '晚上', '夜里', '晚') and hour < 12: hour += 12
    if match.group(2) and match.group(2) in ('中午') and hour < 8: hour += 12
    # print(match.groups(), f"{m1}{(hour):02d}{match.group(4)}{match.group(5)}")
    if match.group(5):
        return f"{m1}{(hour):02d}{match.group(4)}{match.group(5)}"
    else:
        return f"{m1}{(hour):02d}:00"

def exchange_time_match3(match):
    hour = chinese_to_num(match.group(4))
    if match.group(3) and match.group(3) in ('下午', '晚上', '夜里', '晚') and hour < 12: hour += 12
    if match.group(3) and match.group(3) in ('中午') and hour < 8: hour += 12
    # print(match.groups(), f"{m1}{(hour):02d}{match.group(4)}{match.group(5)}")
    if match.group(6):
        return f"{match.group(1)}日{match.group(2)}{(hour):02d}{match.group(5)}{match.group(6)}"
    else:
        return f"{match.group(1)}日{match.group(2)}{(hour):02d}:00"

def exchange_time_value(value, key, data):
        match = re.match(r'([下每]个?月)(\d{1,2}|[一两二三四五六七八九十]{1,3})[号日]([凌早晨上中下午晚夜里]{0,2})(\d{1,2}|[一两二三四五六七八九十]{1,3})(点)(.{0,3})', value)
        if match:
            return exchange_time_match3(match)
        match = re.match(r'([这本下]{0,2}周[一二三四五六七日天]|[今明后][天日]?)?([凌早晨上中下午晚夜里]{0,2})(\d{1,2}|[一两二三四五六七八九十]{1,3})[点](\d{1,2}|[一二三四五六七八九十]{1,3})分', value)
        if match:
            return exchange_time_match0(match)
        match = re.match(r'([这本下]{0,2}周[一二三四五六七日天]|[今明后][天日]?)?([凌早晨上中下午晚夜里]{0,2})(\d{1,2}|[一两二三四五六七八九十]{1,3})[点:](\d{1,2}|[一二三四五六七八九十]{1,3})', value)
        if match:
            return exchange_time_match0(match)
        match = re.match(r'([这本下]{0,2}周[一二三四五六七日天]|[今明后][天日]?)?([凌早晨上中下午晚夜里]{0,2})(\d{1,2}|[一两二三四五六七八九十]{1,3})[点]半', value)
        if match:
            return exchange_time_match1(match)
        match = re.match(r'([这本下]{0,2}周[一二三四五六七日天]|[今明后][天日]?)?([凌早晨上中下午晚夜里]{0,2})(\d{1,2}|[一两二三四五六七八九十]{1,3})(点)(.{0,3})', value)
        if match:
            return exchange_time_match2(match)
        if key == 'remind_time_chinese' and data.get(key) and data.get("start_time"):
            current_time = data.get("current_time")[1:] if data.get("current_time")[0] == '`' else data.get("current_time")
            new_start_time = data.get("start_time")[1:] if data.get("start_time")[0] == '`' else data.get("start_time")
            return exchange_relative_time(data.get("remind_time_chinese"), current_time, new_start_time)
        return value

def exchange_relative_time(time_chinese, current_time, new_start_time):
    if not new_start_time or not time_chinese: return time_chinese
    match = re.match(r'(提前|开始前)(\d{1,2}|[一二三四五六七八九十两半]{1,3})[个]?(分|小时)钟?', time_chinese)
    if match:
        num = chinese_to_num(match.group(2))
        if match.group(3) == '分':
            remind_time = time_add_minute(new_start_time, -1*num)
            return exchange_remind_time(remind_time, current_time)
        elif match.group(3) == '小时':
            remind_time = time_add_minute(new_start_time, -1*num*60)
            return exchange_remind_time(remind_time, current_time)
    return time_chinese

def is_right(num, key, a0, a1, data0, data1):
    if a0 == a1: return True
    if key in ('start_date_chinese', 'start_time_chinese', 'end_date_chinese', 'end_time_chinese', 'remind_date_chinese', 'remind_time_chinese'):
        v0 = exchange_time_value(a0, key, data0)
        v1 = exchange_time_value(a1, key, data1)
        if isinstance(v1, list) and v0 in v1:
            # print(f"[{num+1}] '✓' , 转换: ", v0, v1)
            return True
        elif v0 == v1:
            # print(f"[{num+1}] '✓' , 转换: {a0}={v0}, {a1}={v1}")
            return True
        else:
            print(f"[{num+1}] '✗' , 转换: {a0}={v0}, {a1}={v1}, key={key}")
            # print(data0)
            # print(data1)
            pass
    elif key in ('content'):
        n = 0
        for a in a0:
            if a not in a1: n += 1
        if n <= 1: return True
    return False

def main(file0, file1, rslt):
    answer0 = get_answer_from_file(file0)
    answer1 = get_answer_from_file(file1)
    num = 0
    r = {}
    for idx, data0 in enumerate(answer0):
        data1 = answer1[idx]
        num += 1
        # print(num, data0.get('content'))
        answer_is_right = True
        for key in keys:
            a0 = data0.get(key)
            a1 = data1.get(key)
            if is_right(num, key, a0, a1, data0, data1):
                r[key] = r[key]+1 if r.get(key) else 1
            else:
                if key not in ('memory_subtype', 'place', 'related_person'):
                    answer_is_right = False
                    # print(f"{data0['query_hist']},{data0['current_time'][1:]}")
        if answer_is_right: r['answer'] = r['answer']+1 if  r.get('answer') else 1

    for key in keys+['answer']:
        score = f"{round((r.get(key, 0)/num)*100, 2)}%"
        if rslt.get(key):
            rslt[key].append(score)
        else:
            rslt[key] = [score]

    return rslt







# filename = "集合1-随机生成-评估1000"
# filename = "集合3-专注时间集合-评估500"
filename = "集合4-多轮数据A"
# filename = "集合2-重点例行case"
online_version = ""
# online_version = "/一期线上版本_deepseek_v3"
# online_version = "/一期线上版本_qwen3_plus"
file0 = f"./9_答案/result_{filename}.csv"
file1 = f".{online_version}/1_生成结果/result_{filename}.csv"
print(file0, file1)
rslt = {}
rslt = main(file0, file1, rslt)

print("** 字段的准确率: ")
for key in keys:
    print(f" - {key}: {', '.join(rslt[key])}")
print(f"** 整体的准确率: ")
print(f" - 整体: {', '.join(rslt['answer'])}")
print(f" - 整体准确的定义: 除了记忆子类型、地址、相关人，其他字段全部准确")