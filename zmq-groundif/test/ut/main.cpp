
#include <fprime-zmq/zmq-groundif/ZmqGroundIfComponentImpl.hpp>
#include <fprime-zmq/zmq-groundif/test/ut/Tester.hpp>

volatile bool quit = false;

static void sighandler(int signum){
    quit = true;
}

int main(int argc, char* argv[]){

    signal(SIGINT, sighandler);
    signal(SIGTERM, sighandler);

    Zmq::ZmqGroundIfComponentImpl comp("flight");
    comp.init(100, 1);
    comp.start(1, 90, 20*1024);

    while(not quit){
    
    }

    comp.exit();
    

}

