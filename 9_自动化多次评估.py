import random
import pandas as pd
import json
import re
from datetime import datetime, timedelta



keys = ['memory_type', 'memory_subtype', 'content', 'place', 'related_person', 'start_time_has_hour', 'start_time_not_right', 'start_time', 'end_time', 'remind_time'
        # ,'is_repeat_time', 'repeat_freq', 'repeat_value', 'repeat_last_time'
        ,'start_date_chinese', 'start_time_chinese', 'end_date_chinese', 'end_time_chinese', 'remind_date_chinese', 'remind_time_chinese'
        ]

num_map = {'半': 0.5, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
           '十': 10, '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15, '十六': 16, '十七': 17, '十八': 18, '十九': 19,
           '二十': 20, '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25, '二十六': 26, '二十七': 27,
           '二十八': 28, '二十九': 29, '三十': 30, '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34, '三十五': 35,
           '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40, '四十一': 41, '四十二': 42, '四十三': 43,
           '四十四': 44, '四十五': 45, '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50,
           '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54, '五十五': 55, '五十六': 56, '五十七': 57, '五十八': 58, '五十九': 59, '六十': 60}

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

def get_answer_from_file_json(df):
    answer = []
    df['result'] = df['生成结果'].apply(lambda x: str2json_llm_output(json.loads(x)['result']))
    for i, row in df.iterrows():
        d = row['result']
        v = {}
        for key in keys:
            if key in ('start_time', 'end_time', 'remind_time'):
                if d.get('start_time_has_hour') == '是' and str(d.get('start_time_not_right')) == '0':
                    v[key] = '`'+d.get(key, '') if d.get(key) else ''
                else:
                    v[key] = ''
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
        for key in keys:
            value = str(row[key])
            value = '' if value == 'nan' else value
            if key in ('start_time', 'end_time', 'remind_time'):
                if row['start_time_has_hour'] == '是' and str(row['start_time_not_right']) == '0':
                    v[key] = value if value else ''
                else:
                    v[key] = ''
            else:
                v[key] = value
        answer.append(v)
    return answer

def exchange_time_match0(match):
    hour = match.group(2)
    hour = num_map.get(hour) if num_map.get(hour) else int(hour)
    if match.group(1) in ('下午', '晚上', '夜里') and hour < 12: hour += 12
    minute = match.group(3)
    minute = num_map.get(minute) if num_map.get(minute) else int(minute)
    return f"{(hour):02d}:{(minute):02d}"
def exchange_time_match1(match):
    hour = match.group(2)
    hour = num_map.get(hour) if num_map.get(hour) else int(hour)
    if match.group(1) in ('下午', '晚上', '夜里') and hour < 12: hour += 12
    return f"{(hour):02d}{match.group(3)}{match.group(4)}"

def exchange_time_value(value):
        match = re.match(r'([凌早晨上中下午晚夜里]{0,2})(\d{1,2}|[一二三四五六七八九十]{1,3})[点](\d{1,2}|[一二三四五六七八九十]{1,3})分', value)
        if match:
            return exchange_time_match0(match)
        match = re.match(r'([凌早晨上中下午晚夜里]{0,2})(\d{1,2}|[一二三四五六七八九十]{1,3})[点](\d{1,2}|[一二三四五六七八九十]{1,3})', value)
        if match:
            return exchange_time_match0(match)
        match = re.match(r'([凌早晨上中下午晚夜里]{0,2})(\d{1,2}|[一二三四五六七八九十]{1,3})(点)(.{0,3})', value)
        if match:
            return exchange_time_match1(match)
        return value

def is_right(key, a0, a1, data0, data1):
    if a0 == a1: return True
    if key in ('start_time_chinese', 'end_time_chinese', 'remind_time_chinese'):
        v0 = exchange_time_value(a0)
        v1 = exchange_time_value(a1)
        if v0 == v1:
            print(f"输出: '✓' , 转换: {a0}={v0}, {a1}={v1}")
            return True
        else:
            print(f"输出: '✗' , 转换: {a0}={v0}, {a1}={v1}, key={key}")
            # print(data0)
            # print(data1)
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
        answer_is_right = True
        for key in keys:
            a0 = data0.get(key)
            a1 = data1.get(key)
            if is_right(key, a0, a1, data0, data1):
                r[key] = r[key]+1 if r.get(key) else 1
            else:
                if key not in ('memory_subtype', 'place', 'related_person'):answer_is_right = False
        if answer_is_right: r['answer'] = r['answer']+1 if  r.get('answer') else 1

    for key in keys+['answer']:
        score = f"{round((r.get(key, 0)/num)*100, 2)}%"
        if rslt.get(key):
            rslt[key].append(score)
        else:
            rslt[key] = [score]

    return rslt







# filename = "集合1-随机生成-评估1000"
# filename = "集合4-多轮数据"
# filename = "集合3-专注时间集合-评估500"
filename = "集合2-重点例行case"
file0 = f"./9_答案/{filename}.csv"
file1 = "./1_生成结果/多次跑稳定性/{}_{}.csv"
rslt = {}
for i in range(1, 6):
    rslt = main(file0, file1.format(filename, i), rslt)

print("** 字段的准确率: ")
for key in keys:
    print(f" - {key}: {', '.join(rslt[key])}")
print(f"** 整体的准确率: ")
print(f" - 整体: {', '.join(rslt['answer'])}")
print(f" - 整体准确的定义: 除了记忆子类型、地址、相关人，其他字段全部准确")