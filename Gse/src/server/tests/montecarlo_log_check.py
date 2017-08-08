import os

from dateutil import parser
from datetime import datetime

from server.ServerUtils.server_config import ServerConfig
SERVER_CONFIG = ServerConfig.getInstance()

def check_log(log_path, pass_through_dtime):
    """
    Open log file and find the point where the server stability test moved into 
    passthough phase.

    Once that point is reached, make sure all received increases linearly by one. 

    Returns None if log data is complete.
    Returns The log line if data is incomplete.
    """
    MAX_VAL = 255

    with open(log_path, 'r') as the_file:
        data_expected = {}
        for line in the_file:
            split_s = line.split()
            dt_str  = split_s[0] + " " + split_s[1]  
            curr_dt = parser.parse(dt_str)

            # Start checking data after passthrough_dtime 
            #print split_s
            if(curr_dt >= pass_through_dtime):
                client_name = split_s[4]
                data        = int(split_s[5])
                # If this first data entry, set the data expected to the current 
                # value plus one.
                if(client_name not in data_expected):
                    data_expected[client_name] = data + 1
                else:
                    try:
                        # Assert data is increasing linearly
                        assert data == data_expected[client_name]
                    except AssertionError:
                        print ("Expected: {} Received: {}".format(data_expected[client_name], data))
                        return line
                    
                    # Increment the expected value
                    if(data == MAX_VAL):
                        data_expected[client_name] = 0
                    else:
                        data_expected[client_name] = data + 1

    return None 

def main():
    """
    Test all flight and ground clients for data integrity following
    the monte carlo test.
    
    Important varibales:
    pass_through_dtime: The time the monte carlo test changed to the passthrough
                        phase.
    """
    
    pass_through_dtime = parser.parse("2017-08-07 14:13:23,556") 
    
    server_log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath")
   
    num_flight = 3
    flight_names = ["flight_{}".format(i) for i in range(num_flight)]

    num_ground = 5
    ground_names = ["ground_{}".format(i) for i in range(num_ground)]


    for client_name_list in [flight_names, ground_names]:
        for client_name in client_name_list:
            print("Checking: {}".format(client_name))

            log_path = os.path.join(server_log_path, client_name + ".log")

            assertion = check_log(log_path, pass_through_dtime)
            if(assertion):
                print ("Data integrity error in {}".format(client_name))
                print assertion

    






if __name__ == "__main__":
    main()
