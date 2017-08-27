import os
import time
import logging

from server.ServerUtils.server_config import ServerConfig
from utils.logging_util import GetLogger


GLOBAL_TOGGLE = False # ThroughputAnalyzer is inactive by default
SERVER_CONFIG = ServerConfig.getInstance()


def GlobalToggle(value):
    """
    Toggle ThroughputAnalyzer on/off.
    """
    global GLOBAL_TOGGLE
    GLOBAL_TOGGLE = value

def GetTestPoint(name):
    global GLOBAL_TOGGLE

    if(GLOBAL_TOGGLE is True):
        return TestPoint(name)
    else:
        return DummyPoint(name)

def AggregateTestPoints():
    """
    Aggregate all TestPoint data into one file.
    """
    analysis_path = SERVER_CONFIG.get('filepaths','throughput_analysis_filepath')
    final_report_path = os.path.join(analysis_path, "aggregate.txt")
    final_report = open(final_report_path, "w")
    
    for (path, dirs, files) in os.walk(analysis_path):
        for dir_name in dirs:
            dir_path = os.path.join(analysis_path, dir_name)
            report_path = os.path.join(dir_path, "report.txt")
            try:
                with open(report_path, "r") as f:
                    for line in f:
                        final_report.write(line)
                    final_report.write("\n")

            except IOError:
                print("Unable to open: {}".format(report_path))
                continue

    final_report.close()

def InitializeFolders():
    """
    Ensure test_points start with a clean folder. 
    """
    throughput_folder = SERVER_CONFIG.get("filepaths", "throughput_analysis_filepath") 

    # If throughput_folder exists wipe all test_point folders
    # Else, create throughput_folder 
    if(os.path.exists(throughput_folder)):
        os.system("rm -r {}".format(throughput_folder))
    
    os.mkdir(throughput_folder)


        
class DummyPoint(object):
    def __init__(self, name):
        pass
    def StartAverage(self):
        pass
    def Increment(self, count):
        pass
    def SetAverageThroughput(self):
        pass
    def GetAverageThroughput(self):
        pass
    def StartInstance(self):
        pass
    def SaveInstance(self):
        pass
    def GetInstantOverheadArr(self):
        pass
    def GetInstantThroughputArr(self):
        pass
    def PrintReports(self):
        pass



class TestPoint(object):
    def __init__(self, name):
        self.name = name

        # Setup TestPoint folders
        throughput_folder = SERVER_CONFIG.get("filepaths", "throughput_analysis_filepath") 
        self.test_point_folder = os.path.join(throughput_folder, name)

        # Remove contents of TestPoint's folder if it exists
        if(os.path.exists(self.test_point_folder)):
            os.system("rm -r {}/*".format(test_point_folder))  
        else: # Create folder
            os.mkdir(self.test_point_folder)

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
        """
        Divide the total number of messages by the total time elapsed.
        """
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

        report_path = os.path.join(self.test_point_folder, "report.txt")
        with open(report_path, 'w') as f:
            f.write(self.name + "\n")
            f.write("Application_Throughput {}\n".format(self.__throughput_avg))
            f.write("Average_Instantaneous_Throughput {}\n".format(avg_inst_throughput))
            f.write("Average_Instantaneous_Overhead {}\n".format(avg_inst_overhead))

        instant_path = os.path.join(self.test_point_folder, "instant_tp_measurements.txt")
        with open(instant_path, 'w') as f:
            f.write(self.name + "\n")
            for val in self.__throughput_inst:
                f.write("{}\n".format(val))

        instant_path = os.path.join(self.test_point_folder, "instant_ov_measurements.txt")
        with open(instant_path, 'w') as f:
            f.write(self.name + "\n")
            for val in self.__overhead_inst:
                f.write("{}\n".format(val))


