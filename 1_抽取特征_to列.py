import random
import pandas as pd
import json
import re
from datetime import datetime, timedelta

filename = "集合1-随机生成-评估1000"
# filename = "集合3-专注时间集合-评估500"
# filename = "集合2-重点例行case_llm_plus"
# filename = "集合2-重点例行case"
filename = "集合4-多轮数据"
online_version = ""
# online_version = "/一期线上版本_deepseek_v3"
input_file = f".{online_version}/1_生成结果/{filename}.csv"
output_file = f".{online_version}/1_生成结果/result_{filename}.csv"
print(f"input_file: {input_file}")
print(f"output_file: {output_file}")


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

def get_time_value(value):
    if not value: return ''
    if len(value) == 19:
        return '`'+value
    else:
        return '`'+f"{value[:4]}-{value[4:6]}-{value[6:]}"

def main():
    df = pd.read_csv(input_file)
    df = df.iloc[:, [0,1,-1]]
    df['result'] = df['生成结果'].apply(lambda x: str2json_llm_output(json.loads(x)['result']))
    if not online_version:
        keys = ['memory_type', 'memory_subtype', 'content', 'place', 'related_person', 'start_time_has_hour', 'start_time_not_right',
            'start_time', 'end_time', 'remind_time', 'is_repeat_time', 'repeat_freq', 'repeat_value', 'repeat_last_time'
            ,'start_date_chinese', 'start_time_chinese', 'end_date_chinese', 'end_time_chinese', 'remind_date_chinese', 'remind_time_chinese'
           ]
    # keys = ['memory_type', 'start_time_has_hour', 'start_time_not_right',
    #         'start_time', 'end_time', 'remind_time', 'is_repeat_time', 'repeat_freq', 'repeat_value', 'repeat_last_time']
    else:
        keys = ['memory_type', 'memory_subtype', 'content', 'place', 'related_person', 'start_time_has_hour', 'start_time_not_right',
            'start_time', 'end_time', 'remind_time', 'is_repeat_time', 'repeat_freq', 'repeat_value', 'repeat_last_time'
           ]

    # fo = open(output_file, 'w', encoding="utf-8")
    rslt = []
    for i, row in df.iterrows():
        v = []
        v.append(row['query_hist'])
        v.append('`'+row['current_time'])
        d = row['result']
        for key in keys:
            if key in ('start_time', 'end_time', 'remind_time'):
                if d.get('start_time_has_hour') == '是' or d.get('start_time_is_accurate') == '是' :
                    v.append(get_time_value(d.get(key)))
                else:
                    v.append('')
            elif key == 'start_time_has_hour':
                value = d.get('start_time_is_accurate') if d.get('start_time_is_accurate') else d.get(key, '')
                v.append(str(value))
            else:
                v.append(str(d.get(key, '')))
        rslt.append(v)
        # fo.write("\t".join(v), encoding='utf-8-sig')

    # print(df_yes)
    # df_new = df_yes[['query_hist', 'current_time'] + keys]
    df_new = pd.DataFrame(rslt, columns=[['query_hist', 'current_time'] + keys])

    df_new.to_csv(output_file, encoding='utf-8-sig', index=False)



main()

