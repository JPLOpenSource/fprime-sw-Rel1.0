import logging
from logging import DEBUG, ERROR
import os

GLOBAL_LEVEL = False
GLOBAL_LOG_LEVEL = ERROR
GLOBAL_FILE_LEVEL = ERROR

def SetGlobalLoggingLevel(logLevel, fileLevel, globalLevel=False):
    global GLOBAL_LEVEL
    global GLOBAL_LOG_LEVEL
    global GLOBAL_FILE_LEVEL

    GLOBAL_LEVEL = globalLevel # Let each GetLogger set their own level 
    GLOBAL_LOG_LEVEL = logLevel
    GLOBAL_FILE_LEVEL = fileLevel


def GetLogger(name, logPath, logLevel=DEBUG, fileLevel=DEBUG, chLevel=DEBUG):
    """
    Simple logging utility that retuns a logger
    setup for console and file logging.
    Creates the log in:
        logPath/<name>.log

    Author:  David Kooi 
    Created: April, 2017
    """
    global GLOBAL_LEVEL
    global GLOBAL_LOG_LEVEL
    global GLOBAL_FILE_LEVEL

    if GLOBAL_LEVEL:
        logLevel  = GLOBAL_LOG_LEVEL
        fileLevel = GLOBAL_FILE_LEVEL 

    logger = logging.getLogger(name)
    logger.setLevel(logLevel)
    logger.propagate = False
    
    # Create formatter
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    # Create file handler
    fh = logging.FileHandler(os.path.join(logPath, "{}.log".format(name))) 
    fh.setLevel(fileLevel)
    fh.setFormatter(formatter)

    # Create Console handler 
    ch = logging.StreamHandler()
    ch.setLevel(chLevel) 
    ch.setFormatter(formatter)

    
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
