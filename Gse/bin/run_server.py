import os
import sys
import logging
import argparse

from server.Kernel.kernel import ZmqKernel

def main():
    parser = argparse.ArgumentParser(description="FPrime GSE Server")
    parser.add_argument('cmd_port', metavar='p', type=int, help="Server command port number.")
    parser.add_argument('-v', '--verbose', action="store_true", help="Set verbose logging level.")

    args = parser.parse_args()	

    if(args.verbose):
    	file_lvl = console_lvl = logging.DEBUG
        console_lvl = logging.ERROR
    else:
    	file_lvl = console_lvl = logging.INFO

    kernel = ZmqKernel(args.cmd_port, console_lvl, file_lvl)  
    kernel.Start()


if __name__ == "__main__":
    main()
