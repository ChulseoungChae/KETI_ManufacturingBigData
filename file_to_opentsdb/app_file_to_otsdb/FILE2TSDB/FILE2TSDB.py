#!/usr/bin/env python
#-*- coding: utf-8 -*-

#import requests
import time
import json
from collections import OrderedDict
import pandas as pd
import sys
import os
import argparse
import shutil
import copy
from datetime import datetime

import pcs
import re
#출력 디렉토리 이름을 output으로 변경
# Result, changed JSON 등 , output 디렉토리 하부에 저장
# write 관련 함수는 모듈을 따로 파일로 만들면 좋을것같음

ARG= 50 #argment
'''
    convert Time to Epoch
'''
def checkTimeFormat(_time):
    # YYYY-MM-DD HH:MM:SS.SSS
    patt1=re.compile("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}")
    # YYYY-MM-DD HH:MM:SS
    patt2=re.compile("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    # YYYY-MM-DDTHH:MM:SS.SSS
    patt3=re.compile("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}")
    # YYYYmmddHHMMSS
    patt4 = re.compile("\d{14}")

    # time format 확인 후 epoch로 convert
    if patt1.match(_time):
        # print("YYYY-MM-DD HH:MM:SS.SSS: ",_time)
        epoch=convertMilliTimeToEpoch(_time)
    elif patt2.match(_time):
        # print("YYYY-MM-DD HH:MM:SS: ",_time)
        epoch=convertTimeToEpoch(_time)
    elif patt3.match(_time):
        # print("YYYY-MM-DDTHH:MM:SS.SSS: ",_time)
        epoch=convertMilliTimeToEpoch_v2(_time)
    elif patt4.match(_time):
        # print("YYYYmmddHHMMSS: ",_time)
        epoch=convertTimeToEpoch_v2(_time)
    else:
        print("unusable time format!!")
        sys.exit(1)
    return epoch

# YYYY-mm-dd HH:MM:SS -> epoch
def convertTimeToEpoch(_time):
    date_time = "%s.%s.%s %s:%s:%s" %(_time[8:10], _time[5:7], _time[:4], _time[11:13], _time[14:16], _time[17:19])
    pattern = "%d.%m.%Y %H:%M:%S"
    epoch = int (time.mktime(time.strptime(date_time, pattern)))
    return epoch

# YYYYmmddHHMMSS -> dd.mm.YY HH:MM:SS
def convertTimeToEpoch_v2(_time):
    _time=str(_time)
    date_time = "%s.%s.%s %s:%s:%s" %(_time[6:8], _time[4:6], _time[:4], _time[8:10], _time[10:12], _time[12:])
    pattern = "%d.%m.%Y %H:%M:%S"
    epoch = int (time.mktime(time.strptime(date_time, pattern)))
    return epoch

# YYYY-MM-DD HH:MM:SS.SSS ->epoch
def convertMilliTimeToEpoch(_time):
    date_time = "%s.%s.%s %s:%s:%s.%s" %(_time[8:10], _time[5:7], _time[:4], _time[11:13], _time[14:16], _time[17:19],_time[20:23])
    pattern = "%d.%m.%Y %H:%M:%S.%f"
    print(date_time)
    dt=datetime.strptime(date_time,pattern)
    _ut = datetime.utcfromtimestamp(0)
    delta=dt-_ut
    epoch=int(delta.total_seconds() * 1000)
    return epoch

# YYYY-MM-DDTHH:MM:SS.SSS ->epoch
def convertMilliTimeToEpoch_v2(_time):
    date_time = "%s.%s.%s %s:%s:%s,%s" %(_time[8:10], _time[5:7], _time[:4], _time[11:13], _time[14:16], _time[17:19],_time[20:23])
    pattern = "%d.%m.%Y %H:%M:%S,%f"
    dt=datetime.strptime(date_time,pattern)
    _ut = datetime.utcfromtimestamp(0)
    delta = dt - _ut
    epoch = int(delta.total_seconds() * 1000)
    return epoch

def file2df(_filename, _field, _ts, _carid):
    
    f_extension = os.path.splitext(_filename)[1]
    col=_field+[_ts,_carid]
    print
    if f_extension == '.csv' or f_extension == '.CSV':
        try:
            chunks = pd.read_csv(_filename, usecols = col ,low_memory=False, chunksize=10000, encoding='utf-8')

        except UnicodeDecodeError:
            try:
                chunks = pd.read_csv(_filename,usecols = col, low_memory=False, chunksize=10000, encoding='euc-kr')
            except UnicodeDecodeError:
                chunks = pd.read_csv(_filename, usecols = col, low_memory=False, chunksize=10000, encoding='cp949')
        
        df = pd.concat(chunks, ignore_index=True)
    
    elif f_extension == '.xlsx' or f_extension == '.XLSX':
        df = pd.read_excel(_filename, usecols = col, converters={ts:str})
    else:
        df = []
    _tmp=(", ".join(_field))

    print("\n\n****[Covert File: %s to Dataframe]****" %_filename)
    print("    File: %s\n    Field name: %s\n    DataFrame length: %d" %(_filename,_tmp,len(df)))
    print("************************************************************")
    return df

def pack_to_meta(field, ts, carid, metric, pn, cn, ip,port):
    ret = {}
    ret['field']=field.split('|')
    ret['timestamp']=ts
    ret['carid']=carid
    ret['metric']=metric
    ret['pn']= pn
    ret['cn']= cn
    ret['url']='http://'+ip+':'+port+str('/api/put')
    return ret

def recursive_search_dir(_nowDir, _filelist):
    dir_list = [] # 현재 디렉토리의 서브디렉토리가 담길 list
    f_list = os.listdir(_nowDir)
    print(" [loop] recursive searching ", _nowDir)

    for fname in f_list:
        file_extension = os.path.splitext(fname)[1]
        #print(file_extension)

        if file_extension ==  '.csv' or file_extension == '.CSV' : # csv
            _idx = -4
        elif file_extension ==  '.xlsx' or file_extension == '.XLSX' : # excel
            _idx = -5
        else: continue

        if os.path.isdir(_nowDir+'/'+fname):
            dir_list.append(_nowDir+'/'+fname)
        elif os.path.isfile(_nowDir+'/'+fname):
            if fname[_idx:] == file_extension:
                _filelist.append(_nowDir+'/'+fname)

    for toDir in dir_list:
        recursive_search_dir(toDir, _filelist)


def brush_args():

    _len = len(sys.argv)

    if _len < 9:
        print(" 추가 정보를 입력해 주세요. 위 usage 설명을 참고해 주십시오")
        print(" python 실행파일을 포함하여 아규먼트 갯수 9개 필요 ")
        print(" 현재 아규먼트 %s 개가 입력되었습니다." % (_len))
        print(" check *this_run.sh* file ")
        exit(" You need to input more arguments, please try again \n")

    _field = sys.argv[1]
    _ts = sys.argv[2]
    _carid = sys.argv[3]
    _metric = sys.argv[4]
    _pn = int(sys.argv[5])
    _cn = int(sys.argv[6])
    _ip = sys.argv[7]
    _port = sys.argv[8]


    return _field, _ts,_carid, _metric,_pn,_cn,_ip,_port

if __name__ == "__main__":

    field,ts,carid,metric,pn,cn,ip,port=brush_args()
    file_dir='../files'
    file_list=[]

    recursive_search_dir(file_dir, file_list)

    print("\n--------------------file list--------------------")
    for f in file_list:
        _size=os.path.getsize(f)/(1024.0*1024.0)
        print("file: %s   size: %.3f (MB)" %(f,_size))
        #print(os.path.splitext(f)[1])

    print("\n--------------------------------------------------\n")
    meta = pack_to_meta(field, ts, carid, metric, pn, cn, ip, port)

    # 서브 프로세스 관리자, 생산자, 소비자 생성
    workers = pcs.Workers(pn, cn)
    works_basket_list = workers.start_work(meta)

    start_time=time.time()

    for file_name in file_list:
        # files -> df
        df= file2df(file_name, meta['field'], ts, carid)
        if len(df) == 0:
            continue
        
        elif len(df) < meta['pn']:
            for idx in range(pn):
                while (works_basket_list[idx].full()):
                    time.sleep(0.5)
                if idx == 0:
                    works_basket_list[idx].put(df)
                else:
                    works_basket_list[idx].put('None')

        start=0
        end=start+len(df)//pn

        for idx in range(pn):
            if idx == pn-1:
                end = len(df)
            while (works_basket_list[idx].full()):
                time.sleep(0.5)
            works_basket_list[idx].put(df[start:end])
            start = end
            end = start+len(df)//pn
    print("\nmain : [files -> df] done")
    print("work basket의 모든 data 전송 완료")
    print("subprocess가 아직 실행 중 입니다...\n")

    lines = workers.report()
    totallines=0
    for line in lines:
        totallines += line
    end_time = time.time()
    print("total run time : %f" %(end_time-start_time))
    print("total processed lines : %d" %totallines)