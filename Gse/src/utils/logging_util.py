import logging
from logging import DEBUG
import os



def GetLogger(name, logPath, logLevel=DEBUG, fileLevel=DEBUG, chLevel=DEBUG):
    """
    Simple logging utility that retuns a logger
    setup for console and file logging.
    Creates the log in:
        logPath/<name>.log

    Author:  David Kooi 
    Created: April, 2017
    """

    logger = logging.getLogger(name)
    logger.setLevel(logLevel)
    

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
