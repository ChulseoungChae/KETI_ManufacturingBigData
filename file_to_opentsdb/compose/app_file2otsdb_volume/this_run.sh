#!/bin/bash

# 파이션 코드 실행스크립트
# version 1.1
# 버전 주요 변경 사항 : 아규먼트 18개로 추가

# read 할 csv 정보 및 opentsdb 정보

# [1] target field name
#field="DRIVE_SPEED|DRIVE_LENGTH_TOTAL"
field=$FIELDNAME
# [2] time field name
#ts="RECORD_TIME"
ts=$TIMEFIELD
# [3] id field name
#carid="PHONE_NUM"
carid=$IDFIELD
# [4] opentsdb metric
#metric="test2"
metric=$METRIC
# [5] producer process count
#pn=2
pn=$PN
# [6] consumer process count
#cn=2
cn=$CN

# [7] opentsdb ip
ip=db
#ip='125.140.110.217'
# [8] opentsdb port
port=4242
#port=60010

echo ">>===================================================="
echo "실행 관련 주요 정보(this_run.sh)"
echo "target field name  : "$field
echo "time field name   : "$ts
echo "id field name   : "$carid
echo "metric    : "$metric
echo "pn : "$pn
echo "cn   : "$cn
echo "opentsdb ip : "$ip
echo "opentsdb port    : " $port
echo "====================================================<<"


# time 은 스크립트 SW 실행 시간을 확인하기 위해 사용
# 인자값 7개
#                [1]    [2]   [3] [4]    [5]     [6] [7] [8] [9]
python FILE2TSDB.py $field $ts $carid $metric $pn $cn $ip $port

echo " *** end script run for PYTHON *** "