import os
import sys
from server.Kernel.kernel import ZmqKernel

def main():
    sys.path.append(os.getcwd())

    cmd_port = sys.argv[1] 
       
    kernel = ZmqKernel(cmd_port)  
    kernel.Start()


if __name__ == "__main__":
    main()
