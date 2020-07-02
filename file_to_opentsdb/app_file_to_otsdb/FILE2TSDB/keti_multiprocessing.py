# -*- coding: utf-8 -*-

#from pathos.multiprocessing import ProcessingPool as Pool
#from pathos.helpers import mp
import multiprocessing as mp
import sys


class mproc():
    '''
    This is a class that spawns N new processes to do the designated job

    @initializer params :
        - N : number of processes to spawn
    
        '''

    def __init__(self, N, jobtype='workers'):
        #self.pool = mp.Pool(processes=N, initializer=initializer, initargs=jobtype)
        self.pool = mp.Pool(processes=N)
        self.no_of_prcs = N
        self.STATUS = 'RUNNING'
        #ierr = mp.Value(ctypes.c_int, 0)


    def apply(self, runner, *funcargs):
        
        # 입력 패러미터 확인을 위한 출력
        # print ('<pure>', funcargs, '<pure>')
        
        '''
        Applies the designated job (runner) to the spawned processes

        @params:
            - runner : function to be run
            - args : arguments to be passed to runner function
            '''
        
        try:
            ''' 멀티프로세싱 실행 라인
                Pool 방식으로 멀티프로세싱 실행
                주요 프로그래밍 키워드 in 라이브러리 : multiprocessing pool apply_async get 
                # apply_async => built_in code
                '''
            self.async_results = [ self.pool.apply_async(runner, (funcargs[0], idx, funcargs[1], funcargs[2])) \
                              for idx in range(self.no_of_prcs) ]
            #self.pool.amap
            self.STATUS = 'DONE'
        
        except Exception as e:
            print(e)
            print('Exception occured during apply_async()', __file__)


    def _close(self):
        self.pool.close()
        self.pool.join()


    def get(self, timeout=None):
        '''
            returns result when it's ready
            returns the list of results
                success : list of result
                fail    : empty list

            '''
        self._close()
        rets = [] #list of return values
        if self.STATUS == 'DONE':
            try:
                for result in self.async_results:
                    if timeout: #raise exception if the result is not ready
                        result.successful()
                    rets.append(result.get(timeout))

            #need modification
            except mp.TimeoutError as e:
                print(e)
                raise e

            except AssertionError as e:
                print(e)
                raise e
                
            except Exception as e:
                print(e)
                pass
                #raise e

        return rets