# -*- coding: utf-8 -*-

# Author : https://github.com/CHOBO1
#          https://github.com/jeonghoonkang          

import os
import requests
import time
import json
import multiprocessing
import sys
import copy
import math

# 개발코드 import
import keti_multiprocessing
import FILE2TSDB

def isnan(value):
    try:
        return math.isnan(float(value))
    except:
        return False

# df -> json buffer 
def _produce(works_to_do_list, qidx, works_done, meta):
    print('Producer %d Start Work\n' %os.getpid())
    works_to_do = works_to_do_list[qidx]
    totallines=0
    count=0
    while True:
        while (works_to_do.empty()):
            _pout = ' 프로듀서 큐 Producer queue is empty, wait for 1 \n'
            _pout = __file__ + _pout 
            #sys.stdout.write(_pout)
            #sys.stdout.flush()
            time.sleep (1)

        _pout = ' 프로듀서 큐 Producer queue has data packet  ___________________\n'
        _pout = __file__ + _pout 
        #sys.stdout.write(_pout)
        #sys.stdout.flush()

        #print (help('modules'))

        works = works_to_do.get()  # fpath : csv file path or OpenTSDB return JSON
        # work종료 메시지를 받으면 종료
        if type(works) == type("str") and works == 'END':
            print('Producer %d 종료\n' %os.getpid())
            break
         # 빈 데이터를 받으면 continue
        if type(works) == type("str") and works == 'None':
            continue
        _list = works
        for _field in meta['field']:
            print("\n\n[Convert Dataframe to OpenTsdb json type]\nPID: %d \nFieldname: %s\nDataFrame length: %d"
                  % (os.getpid(), _field, len(_list)))
            _carid = str(_list[meta['carid']].iloc[0])
            dftime = _list[meta['timestamp']].tolist()
            dfval = _list[_field].tolist()

            data_len = len(_list)
            totallines+=data_len
            _buffer = []

            for i in range(len(dftime)):
                value = dfval[i]

                # skip NaN value & ts
                if value == 'nan' or dftime[i] == 'nan':
                    continue
                elif value == 'NaN' or dftime[i] == 'NaN':
                    continue
                elif isnan(value) == True or isnan(dftime[i]) == True:
                    continue
                ts = FILE2TSDB.checkTimeFormat(dftime[i])
                ts = str(ts)
                csv_data = dict()
                csv_data['metric'] = str(meta['metric'])
                csv_data["tags"] = dict()

                csv_data['timestamp'] = ts
                csv_data["value"] = value

                csv_data["tags"]['VEHICLE_NUM'] = _carid
                csv_data["tags"]["fieldname"] = str(_field)

                _buffer.append(csv_data)
                if len(_buffer) == 50:
                    while (works_done.full()):
                        time.sleep(1)
                    works_done.put(copy.deepcopy(_buffer))
                    _buffer=[]

            if len(_buffer) != 0:
                while (works_done.full()):
                    time.sleep(1)
                works_done.put(copy.deepcopy(_buffer))

            count+=1
    
    return totallines


# json buffer -> json file
def _consume(works_to_do, _empty1, meta, _empty2):
    pid = str(os.getpid())
    print('Consumer %s Start Work\n' %pid)
    try:
        sess = requests.Session()
        headers = {'content-type': 'application/json'}

    except requests.ConnectTimeout as e:
        print('ERROR : cannot connect to the server')
        exit()


    while True:
        while (works_to_do.empty()):
            _pout = ' 컨서머 큐 Consumer queue is empty, wait for 1 \n'
            _pout = __file__ + _pout 
            #sys.stdout.write(_pout)
            #sys.stdout.flush()
            time.sleep (1)
        works = works_to_do.get()
        _qsz = works_to_do.qsize()
        if (_qsz % 250) == 0 :
            _pout = '[Put Json to OpenTSDB]PID: %d Queue Size %d ||| \r' %(os.getpid(),_qsz)
            # _pout = '[CONSUMER]PID: %d Queue Size %d PUT Json to OpenTsdb   ||| \r' %(_qsz)
            sys.stdout.write(_pout)
            sys.stdout.flush()
        # 종료
        if works == 'END':
            print('Consumer %s 종료\n' %pid)
            break

        else:
            try:
                response = sess.post(meta['url'], data=json.dumps(works), headers=headers)


                tries = 0
                # 서버로부터 응답이 오긴 하는데 ACK가 아닌 경우
                while (response.status_code > 204):
                    # try to change  50 dps -> 30 dps
                    print ( 'http put error', response, __file__)
                    print(response.text)
                    print("[Process ID] " + pid)
                    
                    if tries > 10:
                        print('Tried count exceed')
                        tries = 0
                        break

                    time.sleep(0.05 * tries)
                    response = sess.post(meta['url'], data=json.dumps(works), headers=headers)  # , timeout=10)
                    tries += 1
                    
            # 서버로부터 아예 응답이 없는 경우
            except requests.ReadTimeout as e:
                retry = 0
                while True:
                    if retry > 10:
                        print('ERROR : NO RESPONSE FROM SERVER. EXITING THIS PROGRAM')
                        exit()
                    try:
                        sess = requests.Session()
                        break
                    except requests.ConnectTimeout as e:
                        retry += 1
                        time.sleep(10)
            
            # 기타 IO 관련 에러
            # 체크할수 있는 플래그가 있어야 하지만, 아직 구현 못함
            # 현재는 Queue max 갯수를 full 로 체크하다가, full 되면 종료시켜 버림
            except IOError as e:
                #shx.value += 1
                print( '#'*3, __file__, 'ERROR : IOError. system exits')
                # to do : 이 경우, 지속적으로 Query 하는 것을 막아줘야 함 
                exit()
        
        
    return True

class Workers:
    '''
    프로세스 관리 클래스

    일반적은 호출 순서는 다음과 같다:
    1. 객체 생성 (__init__)
    2. start_work() : 작업내용 및 정보 제공 (내부적으로 프로세스 생성)
    3. end_work() : 작업 마침표 전송
    4. report() : 프로세스 풀을 닫음

        '''

    def __init__(self, nP, nC):
         
        self.nP = nP
        self.nC = nC

        if nP == 0:
            raise AttributeError('nP should be at least 1')

        # 데이터 송수신 큐 설정
        self.pwork_basket_list=[]
        for _ in range(self.nP):
            self.pwork_basket_list.append(multiprocessing.Manager().Queue())
        self.cwork_basket = multiprocessing.Manager().Queue(maxsize=600000)
        
        
    def start_work(self, meta):

        # 프로듀서, 컨슈머 생성
        self.producers = keti_multiprocessing.mproc(self.nP, 'task1-worker')
        if self.nC != 0:
            self.consumers = keti_multiprocessing.mproc(self.nC, 'task2-worker')

        if self.nP != 0:
            # self.producers 는 mproc 클래스 
            self.producers.apply(_produce, self.pwork_basket_list, self.cwork_basket, \
                                 meta)

        if self.nC != 0:
           self.consumers.apply(_consume, self.cwork_basket, meta, None)

        print('Workers-start success')

        return (self.pwork_basket_list)


    def report(self):
        '''
        프로듀서와 컨슈머 프로세스로부터 결과 리턴
        내부적으로 멀티프로세스 pool을 close, join함
            '''
        for idx in range(self.nP):
            self.pwork_basket_list[idx].put('END')

        if self.nP != 0:
            # except 없이 수행이 잘 되면 제대로 return
            retlist = self.producers.get()

        for idx in range(self.nC):
            self.cwork_basket.put('END')

        if self.nC != 0:
            # except 없이 수행이 잘 되면 제대로 return
            self.consumers.get()

        return retlist
