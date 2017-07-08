/*
 * main.cpp
 *
 *  Created on: Jul 4, 2017
 *      Author: tim
 */

#include <fprime-zmq/zmq-sub/test/ut/Tester.hpp>
#include <Os/Task.hpp>
#include <string.h>

volatile bool quit = false;

static void sighandler(int signum) {
    quit = true;
}


int main(int argc, char* argv[]) {

    signal(SIGINT,sighandler);
    signal(SIGTERM,sighandler);

    Zmq::ZmqSubComponentImpl adapter("sub");

    adapter.init(0);
    adapter.open("127.0.0.1","50000",100,20*1024,0);

    // spin waiting for termination
    while (not quit) {
        Os::Task::delay(1000);
    }

    printf("Quitting\n");

    return 0;
}

