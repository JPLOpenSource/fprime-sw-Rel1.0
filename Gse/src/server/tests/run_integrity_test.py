from subprocess import Popen


def main():
    # Test 1
    num_flight = 1
    num_ground = 1 
    flight_throughput = 100000 # msgs / second
    flight_size =  2000 # byte
    ground_throughput = 100000 #  msgs / second
    ground_size  = 2000 # byte
    monte_time  = 0 # seconds 
    pass_time = 60*5#3600*6 # seconds

    cmd = "python integrity_test.py {nf} {ng} {ft} {fs} {gt} {gs} {mt} {pt}"\
           .format(nf = num_flight, ng = num_ground,\
                   ft = flight_throughput, fs = flight_size,\
                   gt = ground_throughput, gs = ground_size,\
                   mt = monte_time, pt = pass_time)
    process = Popen(args=cmd, shell=True)
    process.wait()

    

if __name__ == "__main__":
    main()
