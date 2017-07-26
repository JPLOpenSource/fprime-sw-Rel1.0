import os
import sys
import argparse

from server.Kernel.kernel import ZmqKernel

def main():
    parser = argparse.ArgumentParser(description="FPrime GSE Server")
    parser.add_argument('cmd_port', metavar='p', type=int, help="Server command port number.")

    args = parser.parse_args()	

    kernel = ZmqKernel(args.cmd_port)  
    kernel.Start()


if __name__ == "__main__":
    main()
