/*
 * main.cpp
 *
 *  Created on: Jul 4, 2017
 *      Author: tim
 */

#include <fprime-zmq/zmq-pub/test/ut/Tester.hpp>
#include <Os/Task.hpp>
#include <string.h>

volatile bool quit = false;

static void sighandler(int signum) {
    quit = true;
}


int main(int argc, char* argv[]) {

    signal(SIGINT,sighandler);
    signal(SIGTERM,sighandler);

    Zmq::ZmqPubComponentImpl adapter("pub");

    adapter.init(10,100,0);
    adapter.open("50000");
    adapter.start(0, 100, 20*1024);

    // feed packets to publisher
    while (not quit) {
        Os::Task::delay(1000);
        Fw::InputSerializePort* port = adapter.get_PortsIn_InputPort(0);
        Zmq::ZmqPubComponentImpl::ZmqSerialBuffer buff;
        buff.serialize((U32)10);
        port->invokeSerial(buff);
    }

    printf("Quitting\n");

    adapter.exit();

    return 0;
}

