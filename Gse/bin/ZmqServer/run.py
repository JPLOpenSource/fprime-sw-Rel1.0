import os
import sys
from Kernel.kernel import ZmqKernel

def main():
    sys.path.append(os.getcwd())


    cmd_port = sys.argv[1] 
       
    kernel = ZmqKernel(cmd_port) 
    context = kernel.GetContext()
     
    kernel.Start()

if __name__ == "__main__":
    main()
