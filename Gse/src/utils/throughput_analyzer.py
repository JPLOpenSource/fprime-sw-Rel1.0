import os
import time
import logging

from server.ServerUtils.server_config import ServerConfig
from utils.logging_util import GetLogger


SERVER_CONFIG = ServerConfig.getInstance()

class ThroughputAnalyzer(object):
    def __init__(self, name):
        # Setup Logger  
        self.name = name
        log_dir = SERVER_CONFIG.get("filepaths", "throughput_analysis_filepath") 
        self.log_path = os.path.join(log_dir, name)

        # If path exists wipe logs
        if(os.path.exists(self.log_path)):
            logs = os.path.join(self.log_path, "*.log")
            os.system("rm {}".format(logs))
        else:
            os.mkdir(self.log_path)

        self.__start_time_avg = 0
        self.__delta_avg      = 0
        self.__throughput_avg = 0
        self.__count          = 0

        self.__start_time_inst = 0
        self.__delta_inst      = 0
        self.__overhead_inst    = []
        self.__throughput_inst     = []


    def StartAverage(self):
        """
        Start at the beginning of the process
        """
        self.__start_time_avg = time.time()
    def Increment(self, count):
        """
        Increment the number of units that have passed through
        """
        self.__count += count
        
    def SetAverageThroughput(self):
        self.__delta_avg = time.time() - self.__start_time_avg
        self.__throughput_avg = self.__count / self.__delta_avg

    def GetAverageThroughput(self):
        """
        Return average throughput since latest SetTimeAverage.
        """
        return self.__throughput_avg

    def StartInstance(self):
        """
        Start timing for an instance measurement
        """
        self.__start_time_inst = time.time()
    def SaveInstance(self):
        """
        Save the overhead of one message
        """
        overhead = time.time() - self.__start_time_inst
        self.__overhead_inst.append(overhead)
        try:
            self.__throughput_inst.append(1/overhead)
        except ZeroDivisionError:
            pass
    def GetInstantOverheadArr(self):
        """
        Return array of instant overheads.
        """
        return self.__overhead_inst
    def GetInstantThroughputArr(self):
        """
        Return array of instant throughputs
        """
        return self.__throughput_inst
    def PrintReports(self):
        # Get Averages
        try:
            avg_inst_throughput = sum(self.__throughput_inst) / float(len(self.__throughput_inst))
        except ZeroDivisionError:
            avg_inst_throughput = 0

        try:
            avg_inst_overhead   = sum(self.__overhead_inst) / float(len(self.__overhead_inst))
        except ZeroDivisionError:
            avg_inst_overhead = 0

        report_path = os.path.join(self.log_path, "report.txt")
        with open(report_path, 'w') as f:
            f.write(self.name + "\n")
            f.write("Application_Throughput {}\n".format(self.__throughput_avg))
            f.write("Average_Instantaneous_Throughput {}\n".format(avg_inst_throughput))
            f.write("Average_Instantaneous_Overhead {}\n".format(avg_inst_overhead))

        instant_path = os.path.join(self.log_path, "instant_tp_measurements.txt")
        with open(instant_path, 'w') as f:
            f.write(self.name + "\n")
            for val in self.__throughput_inst:
                f.write("{}\n".format(val))

        instant_path = os.path.join(self.log_path, "instant_ov_measurements.txt")
        with open(instant_path, 'w') as f:
            f.write(self.name + "\n")
            for val in self.__overhead_inst:
                f.write("{}\n".format(val))


