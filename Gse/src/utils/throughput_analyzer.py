import time

from server.ServerUtils.server_config import ServerConfig
from utils.logging_util import GetLogger


SERVER_CONFIG = ServerConfig.getInstance()

class ThroughputAnalyzer(object):
    def __init__(self, name):
        # Setup Logger  
        self.name = name
        self.log_path = SERVER_CONFIG.get("filepaths", "throughput_analysis_filepath") 
        logger = GetLogger("{}".format(name),self.log_path, chLevel=logging.INFO) 
        logger.debug("Logger Active") 


        self.__start_time_avg = 0
        self.__delta_avg      = 0
        self.__throughput_avg = 0
        self.__count          = 0

        self.__start_time_inst = 0
        self.__delta_inst      = 0
        self.__latency_inst    = []
        self.__thrput_inst     = []


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
    def SetTimeAverage(self):
        """
        Set current time.
        """
        self.__delta_avg = time.time() - self.__start_time_avg
    def SetAverageThroughput(self):
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
        self.__thrput_inst.append(1/overhead)

    def GetInstantOverheadArr(self):
        """
        Return array of instant overheads.
        """
        return self.__overhead_inst
    def GetInstantThroughputArr(self):
        """
        Return array of instant throughputs
        """
        return self.__thrput_inst
    def PrintReports(self):
        report_path = os.path.join(self.log_path, "report.txt")
        with open(report_path) as f:
            f.write(self.name + "\n")
            f.write("Average_Throughput {}".format(self.__throughput_avg))

        instant_path = os.path.join(self.log_path, "instant_tp_measurements.txt")
        with open(instant_path) as f:
            f.write(self.name + "\n")
            for val in self.__thrput_inst:
                f.write("{}\n".format(val))

        instant_path = os.path.join(self.log_path, "instant_ov_measurements.txt")
        with open(instant_path) as f:
            f.write(self.name + "\n")
            for val in self.__overhead_inst:
                f.write("{}\n".format(val))


