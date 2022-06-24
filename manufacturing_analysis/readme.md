# Manufacturing Analysis
#### 개요

  - 제조 빅데이터 분석 수행 기능    
    - 원본 데이터파일을 읽어 파일을 하나로 통합 -> 문자로 구성된 'part_num'를 숫자로 변경(문자, 숫자 매칭 테이블 csv 파일로 출력 -> 'part_num_matching.csv') -> device_id > part_number > parts_count 순으로 루프돌며 각 part_num, parts_count 별로 시작/끝 시간, feed_rate 통계, spindle_rate 통계, 실제 가동시간(초)의 정보 계산 및 파일로 저장('statis.csv')

  - 터미널 출력 정보
    - 각 설비별 피로도
    - 각 설비별 최고 피로도를 가지는 part_num
    - 각 설비별 최고 피로도를 가지는 part_count
    - 각 설비별 최고 피로도를 가지는 운영시간


## 사전준비

- Docker Desktop 및 docker-compose 실행 가능해야 함

  1.  리눅스/우분투 docker/docker-compose 설치
  
      https://hcnam.tistory.com/25
      
  2. 윈도우
  
     - docker/docker-compose 설치
  
       https://steemit.com/kr/@mystarlight/docker
     
     - 도커 툴박스 설치

       https://github.com/docker/toolbox/releases

  
## 소프트웨어 실행 방법
### github code로 실행

1. github repo clone 혹은 zip 파일 다운로드

    - git clone
        ```
        $ git clone https://github.com/ChulseoungChae/KETI_ManufacturingBigData.git
        ```

    - 아래링크에서 zip파일 다운로드 후 압축해제, 원하는 디렉토리 생성
    
        [Link (https://github.com/ChulseoungChae/KETI_ManufacturingBigData/releases)](https://github.com/ChulseoungChae/KETI_ManufacturingBigData/releases)
    
        - 또는, wget으로 직접 다운로드후 압축해제
    
        ```
        $ mkdir mount_file
        $ cd mount_file
        $ wget https://github.com/ChulseoungChae/KETI_ManufacturingBigData/releases/download/latest/1_machine.zip
        $ unzip 1_machine.zip
        ```
    
2. file_to_opentsdb compose 디렉토리로 이동
  ```
  $ cd (깃허브 다운로드 경로)/KETI_ManufacturingBigData/KETI_ManufacturingBigData/manufacturing_analysis/1_machine/
  ```

3. python 코드 실행
  ```
  $ python3 manufacturing_analysis.py
  ```

### docker image를 다운로드하여 실행
  - docker image 다운로드
    ```
    docker pull cschae1123/machine_analysis
    ```

  - 다운로드받은 docker image 실행
    ```
    docker run -it --name docker-machine -v (깃허브 다운로드 경로)/KETI_ManufacturingBigData/manufacturing_analysis/1_machine/v_sharing:/app/machine_analysis/result/ machine_analysis:latest
    ```


## 컨테이너 실행 후 결과 확인
  - 터미널 출력 혹은 공유폴더에 생성된 출력파일 확인
    ```
    $ cd (깃허브 다운로드 경로)/KETI_ManufacturingBigData/manufacturing_analysis/1_machine/v_sharing

    result.txt 파일 확인
    ```

    - 출력 텍스트 예시
    ```
    --------------------------------------------------
    BYE-164의 총 피로도 : 361658.20830279804
    BYE-164의 최고 피로도를 가지는 part_num : 16
    BYE-164의 최고 피로도를 가지는 part_count : 380
    BYE-164의 최고 피로도를 가지는 운영시간 : 350540
    --------------------------------------------------

    --------------------------------------------------
    BYE-166의 총 피로도 : 165.80072860883243
    BYE-166의 최고 피로도를 가지는 part_num : 24
    BYE-166의 최고 피로도를 가지는 part_count : 247
    BYE-166의 최고 피로도를 가지는 운영시간 : 33781
    --------------------------------------------------

    --------------------------------------------------
    BYE-161의 총 피로도 : 1.4175293387871637
    BYE-161의 최고 피로도를 가지는 part_num : 44
    BYE-161의 최고 피로도를 가지는 part_count : 61
    BYE-161의 최고 피로도를 가지는 운영시간 : 18360
    --------------------------------------------------
    ```


## 도커 컨테이너 내부 코드 수정 및 수정한 코드 실행
  1. 일시정지된 docker container 실행 </br>
    ```
    $ docker start docker-machine
    ```

  2. docker container 접속 </br>
    ```
    $ docker exec -it docker-machine bash
    ```

  3. 메인 코드에서 코드 수정 </br>
    ```
    $ vi manufacturing_analysis.py
    ```

  4. 수정한 코드가 적용된 코드 실행 </br>
    ```
    $ python3 manufacturing_analysis.py
    ```
