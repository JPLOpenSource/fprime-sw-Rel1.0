
from subprocess import Popen


def main():
    """
    Define a test to perform.
    Parameters:
    num_flight: Number of flight clients
    num_ground: Number of ground clients
    message_size: Number of bytes per message
    flight_throughput: Used to set speed of message transmission. 
    NOTE: This is not the real throughput the OS grants.
          Check the throughput logs to check real throughput
    monte_time: How long to perform random connections and disconnections between
              the flight and ground clients.
    pass_time: How long to pass data between clients.
    """
    # Test 1
    num_flight = 1
    num_ground = 5 
    message_size = 20
    flight_throughput = 100 # msgs / second
    monte_time  = 0 # seconds 
    pass_time = 30#60*5#3600*6 # seconds

    cmd = "python integrity_test.py {nf} {ng} {ft} {fs} {gt} {gs} {mt} {pt}"\
           .format(nf = num_flight, ng = num_ground,\
                   ft = flight_throughput, fs = message_size,\
                   gt = 0, gs = message_size,\
                   mt = monte_time, pt = pass_time)
    process = Popen(args=cmd, shell=True)
    process.wait()

    

if __name__ == "__main__":
    main()
