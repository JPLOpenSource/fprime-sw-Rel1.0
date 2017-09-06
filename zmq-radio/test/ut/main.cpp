
#include <fprime-zmq/zmq-radio/test/ut/Tester.hpp>

volatile bool quit = false;

static void sighandler(int signum){
    quit = true;
}

int main(int argc, char* argv[]){

    signal(SIGINT, sighandler);
    signal(SIGTERM, sighandler);

    Zmq::Tester tester;
    tester.testConnection();

    //Zmq::ZmqRadioComponentImpl comp("flight");
    //comp.init(100, 1);
    //comp.open("localhost", 5555, "flight_1");
    


    //comp.start(1, 90, 20*1024);

    while(not quit){
    
    }

    //comp.exit();
    

}

