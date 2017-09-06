#!/usr/bin/python

import utils.PortFinder
import sys
import subprocess
import os
import time
import signal
from optparse import OptionParser

def main(argv=None):
    
    start_port = 50000
    end_port = 50100
    used_port = None
    addr = "127.0.0.1" 
    nobin = False
    
    #if len(sys.argv) > 1:
    #    if sys.argv[1] == "-nobin":
    #        print("Not starting binary.")
    #        nobin = True
    
    python_bin = os.environ["PYTHON_BASE"] + "/bin/python"
    
    for port in range(start_port,end_port):
        if not utils.PortFinder.IsPortUsed(port):
            used_port = port
            print("Using port %d"%used_port)
            break;
        
    if (used_port == None):
        print("Could not find port in range %d to %d",start_port,end_port)
        return -1
    
    build_root = os.environ["BUILD_ROOT"]
    
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", action="store", type="int", help="Set the threaded TCP socket server port [default: %default]", default=used_port)
    parser.add_option("-a", "--addr", dest="addr", action="store", type="string", help="set the threaded TCP socket server address [default: %default]", default=addr)
    parser.add_option("-n", "--nobin", dest="nobin", action="store_true", help="Disables the binary app from starting [default: %default]", default=False)
    parser.add_option("-t", "--twin", dest="twin", action="store_true", help="Runs ZmqServer in window, otherwise backgrounds [default: %default]", default=False)

    (opts, args) = parser.parse_args(argv)
    used_port = opts.port
    nobin = opts.nobin
    addr = opts.addr
    twin = opts.twin
#     print 'nobin =', nobin
#     print 'port = ', used_port
#     print 'addr = ', addr 

    # run ZmqServer 
    if twin:
        TTS_args = [python_bin,"%s/Gse/bin/pexpect_runner.py"%build_root,"ZmqServer.log","ZmqServer",python_bin,"%s/Gse/bin/run_server.py"%build_root,"%d"%used_port]
        TTS = subprocess.Popen(TTS_args)
    else:
        tts_log = open("ZmqServer.log",'w')
        TTS_args = [python_bin, "-u", "%s/Gse/bin/run_server.py"%build_root,"%d"%used_port]
        TTS = subprocess.Popen(TTS_args,stdout=tts_log,stderr=subprocess.STDOUT)
    
    # wait for TCP Server to start
    time.sleep(5)
    
    # run Gse GUI
    GUI_args = [python_bin,"%s/Gse/bin/pexpect_runner.py"%build_root,"gui_1.log","GUI 1",python_bin,"%s/Gse/bin/gse.py"%build_root,"--port","%d"%used_port,"--dictionary","%s/Gse/generated/Ref"%build_root,"--connect","--addr",addr,"-L","%s/Ref/logs"%build_root,\
                "-N gui_1"]
    #print ("GUI: %s"%" ".join(GUI_args))
    GUI1 = subprocess.Popen(GUI_args)

    GUI_args = [python_bin,"%s/Gse/bin/pexpect_runner.py"%build_root,"gui_2.log","GUI 2",python_bin,"%s/Gse/bin/gse.py"%build_root,"--port","%d"%used_port,"--dictionary","%s/Gse/generated/Ref"%build_root,"--connect","--addr",addr,"-L","%s/Ref/logs"%build_root,\
                "-N gui_2"]
    GUI2 = subprocess.Popen(GUI_args)


    
    # run two Ref apps
    
    op_sys = os.uname()[0]
    
    ref_bin = "%s/Ref/%s/Ref"%(build_root,os.environ["OUTPUT_DIR"])
    
    if not nobin:
        REF_args = [python_bin,"%s/Gse/bin/pexpect_runner.py"%build_root,"Ref.log","Ref 1 Application",ref_bin,"-p","%d"%used_port,"-a",addr,"-n flight_1"]
        REF1 = subprocess.Popen(REF_args)

        REF_args = [python_bin,"%s/Gse/bin/pexpect_runner.py"%build_root,"Ref.log","Ref 2 Application",ref_bin,"-p","%d"%used_port,"-a",addr,"-n flight_2"]
        REF2 = subprocess.Popen(REF_args)
    
    GUI1.wait()
    GUI2.wait()

    if not nobin:
        try:
            REF1.send_signal(signal.SIGTERM)
            REF2.send_signal(signal.SIGTERM)

        except:
            pass
            
        try:
            REF1.wait()
            REF2.wait()
        except:
            pass
            
    try:
        TTS.send_signal(signal.SIGINT)
    except:
        pass
        
    try:
        TTS.wait()
    except:
        pass
            
    # Run Gse interface
    
            
         

if __name__ == "__main__":
    sys.exit(main())
