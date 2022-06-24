# -*- coding: utf-8 -*-

import time
import pandas as pd
import sys
import os
from datetime import datetime

# 1세부 기계 분석 모듈 임포트
from machine_analysis import MachineAnalysis


def brush_args():
    _csvpath = sys.argv[1]
    _field = sys.argv[2]
    _ts = sys.argv[3]
    _tag = sys.argv[4]

    return _csvpath, _field, _ts, _tag


def convertEpochToTSDBtime(_timestamp, _option=None):
    _timestamp = int(_timestamp)
    datetimeobj = str(datetime.fromtimestamp(_timestamp))
    tsdb_time = "%s/%s/%s-%s:%s:%s" % (datetimeobj[:4], datetimeobj[5:7], datetimeobj[8:10], datetimeobj[11:13], datetimeobj[14:16], datetimeobj[17:19])
    return tsdb_time


def recursive_search_dir(_nowDir, _filelist):
    print("[loop] recursive searching ", _nowDir)

    if os.path.isfile(_nowDir):
        file_extension = os.path.splitext(_nowDir)[1]
        if file_extension == ".csv" or file_extension == ".CSV" or file_extension == ".xlsx":
            _filelist.append(_nowDir)
        return None

    dir_list = []  # 현재 디렉토리의 서브디렉토리가 담길 list
    f_list = os.listdir(_nowDir)
    for fname in f_list:
        file_extension = os.path.splitext(fname)[1]
        if os.path.isdir(_nowDir + "/" + fname):
            dir_list.append(_nowDir + "/" + fname)
        elif os.path.isfile(_nowDir + "/" + fname):
            if file_extension == ".csv" or file_extension == ".CSV" or file_extension == ".xlsx":
                _filelist.append(_nowDir + "/" + fname)

    for toDir in dir_list:
        recursive_search_dir(toDir, _filelist)


def file2df(_filename, _field, _ts, _tag):
    f_extension = os.path.splitext(_filename)[1]

    if f_extension == ".csv" or f_extension == ".CSV":
        if _field == '...' or _tag == 'none':
            try:
                chunks = pd.read_csv(_filename, low_memory=False, chunksize=10000)
            except UnicodeDecodeError:
                try:
                    chunks = pd.read_csv(_filename, low_memory=False, chunksize=10000, encoding="utf-8")
                except UnicodeDecodeError:
                    try:
                        chunks = pd.read_csv(_filename, low_memory=False, chunksize=10000, encoding="euc-kr")
                    except UnicodeDecodeError:
                        chunks = pd.read_csv(_filename, low_memory=False, chunksize=10000, encoding="cp949")
        else:
            col = _field + _ts
            if _tag == 'none' or _tag == 'NONE' or _tag == 'None' or _tag == ['none']:
                None
            else:
                col = col + _tag
            try:
                chunks = pd.read_csv(_filename, usecols=col, low_memory=False, chunksize=10000)
            except UnicodeDecodeError:
                try:
                    chunks = pd.read_csv(_filename, usecols=col, low_memory=False, chunksize=10000, encoding="utf-8")
                except UnicodeDecodeError:
                    try:
                        chunks = pd.read_csv(_filename, usecols=col, low_memory=False, chunksize=10000, encoding="euc-kr")
                    except UnicodeDecodeError:
                        chunks = pd.read_csv(_filename, usecols=col, low_memory=False, chunksize=10000, encoding="cp949")
                        

        df = pd.concat(chunks, ignore_index=True)

    elif f_extension == ".xlsx" or f_extension == ".XLSX":
        df = pd.read_excel(_filename, header=1, usecols=lambda x: 'Unnamed' not in x)
    else:
        df = []

    print("-------------------------------------------------------------")
    print("Convert File to Dataframe")
    print("DataFrame length: %d" % (len(df)))
    print("-------------------------------------------------------------\n")
    return df


# 지정 디렉토리 하위 파일을 데이터프레임으로 변경, 하나의 데이터프레임으로 통합
def file_integration(_file_list, fields, ts, tags):
    print("\n--------------------file integration--------------------\n")
    icnt=0
    for file_name in _file_list:
        icnt += 1
        print("[%d / %d] read %s"  %(icnt,tot_f_len, file_name) )
        
        df = file2df(file_name, fields, ts, tags)
        if icnt == 1: integrated_df = df
        else : integrated_df = pd.concat([integrated_df, df])
    
    # 데이터프레임의 NaN인 셀을 unknown으로 채우기
    nan_filled_df = integrated_df.fillna('unknown')
    
    return nan_filled_df


# part_num 컬럼 str -> number
def part_num2numeric(_integrated_df):
    part_num_unique_list = sorted(list(_integrated_df['part_number'].unique()))
    temp_dict = dict()
    _num = 0
    for _part in part_num_unique_list:
        _num += 1
        temp_dict[_part] = _num

    part_num_df = pd.DataFrame(list(temp_dict.items()), columns=['part_num', 'part_num_new'])
    # part_num 를 숫자로 변경한 매칭테이블 저장
    part_num_df.to_csv('part_num_matching.csv', index=False)
    
    new_part_num = []
    part_num_list = _integrated_df['part_number'].to_list()
    for _s in part_num_list:
        new_part_num.append(temp_dict[_s])

    _integrated_df['part_num_new'] = new_part_num

    return _integrated_df

if __name__ == '__main__':
    # csvpath, fields, ts, tags = brush_args()
    
    csvpath = './data'
    fields = 'feed_rate|spindle_rate'
    ts = 'timestamp'
    tags = 'none'
    div_col1 = 'device_id'
    div_col2 = 'part_num_new'
    div_col3 = 'parts_count'
    # 지정 디렉토리 파일 탐색
    file_list = []
    recursive_search_dir(csvpath, file_list)

    # 각 파일의 용량 및 데이터 길이 표시
    tot_f_len = len(file_list) 
    print ( "total csv file input amount = ", tot_f_len)
    print("\n--------------------file list--------------------")
    for f in file_list:
        _size = os.path.getsize(f) / (1024.0 * 1024.0)
        print("file: %s   size: %.3f (MB)" % (f, _size))
    print("--------------------------------------------------\n")

    # 지정 디렉토리 하위 파일을 데이터프레임으로 변경, 하나의 데이터프레임으로 통합
    integrated_df = file_integration(file_list, fields, ts, tags)
    
    # part_num 컬럼 str -> number
    final_df = part_num2numeric(integrated_df)
    # print(final_df.reset_index(drop=True))
    
    machine_statistics = MachineAnalysis(final_df, ts, fields, div_col1, div_col2, div_col3)
    statis_list = machine_statistics.divide_sort()
    statis_df = pd.DataFrame(statis_list)
    statis_df['feed_rate_per'] = statis_df['feed_rate_sum'] / statis_df['feed_rate_sum'].max()
    statis_df['spindle_rate_per'] = statis_df['spindle_rate_sum'] / statis_df['spindle_rate_sum'].max()
    statis_df['dist_per'] = statis_df['dist_sum'] / statis_df['dist_sum'].max()
    statis_df['tool_fatigue'] = statis_df['operation_time_sec'] * statis_df['feed_rate_per'] * statis_df['spindle_rate_per'] * statis_df['dist_per']

    # statis_df.to_csv('statis.csv', index=False)
    
    print("\n======================설비별 피로도 정보======================")
    
    devid_list = list(statis_df[div_col1].unique())
    with open('./result/result_file.txt', 'w') as f:
        for _id in devid_list:
            devid_df = statis_df.query("%s == '%s'" %(div_col1, _id))
            max_fatigue_df = devid_df.iloc[devid_df['tool_fatigue'].argmax()]
            print("\n--------------------------------------------------")
            print('%s의 총 피로도 : %s' %(_id, devid_df['tool_fatigue'].sum()))
            print('%s의 최고 피로도를 가지는 part_num : %s' %(_id, max_fatigue_df['part_num_new']))
            print('%s의 최고 피로도를 가지는 part_count : %s' %(_id, max_fatigue_df['parts_count']))
            print('%s의 최고 피로도를 가지는 운영시간 : %s' %(_id, max_fatigue_df['operation_time_sec']))
            print("--------------------------------------------------", flush=True)
            f.write("\n--------------------------------------------------\n")
            f.write('%s의 총 피로도 : %s\n' %(_id, devid_df['tool_fatigue'].sum()))
            f.write('%s의 최고 피로도를 가지는 part_num : %s\n' %(_id, max_fatigue_df['part_num_new']))
            f.write('%s의 최고 피로도를 가지는 part_count : %s\n' %(_id, max_fatigue_df['parts_count']))
            f.write('%s의 최고 피로도를 가지는 운영시간 : %s\n' %(_id, max_fatigue_df['operation_time_sec']))
            f.write("--------------------------------------------------")
        
        
    print("\n=============================================================")