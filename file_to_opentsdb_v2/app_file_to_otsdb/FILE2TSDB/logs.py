# -*- coding: utf-8 -*-
import logging
import multiprocessing

# log 파일 용량이 500메가 바이트 초과 시 해당 파일을 백업하고, 새로운 파일에 로그를 저장. 백업된 파일을 갯수 1개로 지정
def get_logger(lname=None,filename="./static/run_log.log",format='[%(levelname)s|%(funcName)s] [%(asctime)s] %(message)s' ):
    # format = '[%(levelname)s | %(filename)s: %(lineno)s] [%(asctime)s] %(message)s\n'
    # logger = multiprocessing.get_logger()

    logger=logging.getLogger(lname)
    '''
    logger의 경우 싱글톤 패턴을 사용하므로
    같은 logger 이름일 경우 handler를 추가하지 않고,
    기존의 logger 객체 return
    '''
    if len(logger.handlers) > 0:
        return logger  # Logger already exists
    fileHandler = logging.FileHandler(filename=filename, mode = 'w')
    formatter = logging.Formatter(format)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.INFO)
    return logger


def write_log(logger,level,message):
    if level==logging.INFO:
        logger.setLevel(level)
        logger.info(message)
    elif level==logging.DEBUG:
        logger.setLevel(level)
        logger.debug(message)
    elif level==logging.WARNING:
        logger.setLevel(level)
        logger.warning(message)
    elif level==logging.ERROR:
        logger.setLevel(level)
        logger.error(message)
    elif level==logging.CRITICAL:
        logger.setLevel(level)
        logger.critical(message)
    else:
        print("unusable log level: %s"%level)