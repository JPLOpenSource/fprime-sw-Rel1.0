#include <Components.hpp>


#include <Fw/Types/Assert.hpp>
#include <Ref/Top/TargetInit.hpp>
#include <Os/Task.hpp>
#include <Os/Log.hpp>
#include <Fw/Types/MallocAllocator.hpp>

#if defined TGT_OS_TYPE_LINUX || TGT_OS_TYPE_DARWIN
#include <getopt.h>
#include <stdlib.h>
#include <ctype.h>
#endif
// List of context IDs

enum {
    DOWNLINK_PACKET_SIZE = 500,
    DOWNLINK_BUFFER_STORE_SIZE = 2500,
    DOWNLINK_BUFFER_QUEUE_SIZE = 5,
    UPLINK_BUFFER_STORE_SIZE = 3000,
    UPLINK_BUFFER_QUEUE_SIZE = 30
};

enum {
        ACTIVE_COMP_1HZ_RG,
        ACTIVE_COMP_P5HZ_RG,
        ACTIVE_COMP_P25HZ_RG,
        ACTIVE_COMP_CMD_DISP,
        ACTIVE_COMP_CMD_SEQ,
        ACTIVE_COMP_LOGGER,
        ACTIVE_COMP_TLM,
        ACTIVE_COMP_PRMDB,
        ACTIVE_COMP_FILE_DOWNLINK,
        ACTIVE_COMP_FILE_UPLINK,

        ACTIVE_COMP_BLKDRV,
        ACTIVE_COMP_PING_RECEIVER,

        CYCLER_TASK,
        ACTIVE_ZMQ_RADIO,
        NUM_ACTIVE_COMPS
};

// Registry
#if FW_OBJECT_REGISTRATION == 1
static Fw::SimpleObjRegistry simpleReg;
#endif

// Component instance pointers
static NATIVE_INT_TYPE rgDivs[] = {1,2,4};
Svc::RateGroupDriverImpl rateGroupDriverComp(
#if FW_OBJECT_NAMES == 1
                    "RGDvr",
#endif
                    rgDivs,FW_NUM_ARRAY_ELEMENTS(rgDivs));

static NATIVE_UINT_TYPE rg1Context[] = {0,0,0,0,0,0,0,0,0,0};
Svc::ActiveRateGroupImpl rateGroup1Comp
#if FW_OBJECT_NAMES == 1
                    ("RG1",rg1Context,FW_NUM_ARRAY_ELEMENTS(rg1Context));
#else
                    (rg1Context,FW_NUM_ARRAY_ELEMENTS(rg1Context));
#endif
;

static NATIVE_UINT_TYPE rg2Context[] = {0,0,0,0,0,0,0,0,0,0};
Svc::ActiveRateGroupImpl rateGroup2Comp
#if FW_OBJECT_NAMES == 1
                    ("RG2",rg2Context,FW_NUM_ARRAY_ELEMENTS(rg2Context));
#else
                    (rg2Context,FW_NUM_ARRAY_ELEMENTS(rg2Context));
#endif
;

static NATIVE_UINT_TYPE rg3Context[] = {0,0,0,0,0,0,0,0,0,0};
Svc::ActiveRateGroupImpl rateGroup3Comp
#if FW_OBJECT_NAMES == 1
                    ("RG3",rg3Context,FW_NUM_ARRAY_ELEMENTS(rg3Context));
#else
                    (rg3Context,FW_NUM_ARRAY_ELEMENTS(rg3Context));
#endif
;


Zmq::ZmqRadioComponentImpl zmqRadio
#if FW_OBJECT_NAMES == 1
                    ("ZRAD")
#endif
;

// Driver Component
Drv::BlockDriverImpl blockDrv
#if FW_OBJECT_NAMES == 1
                    ("BDRV")
#endif
;

// Reference Implementation Components

Ref::RecvBuffImpl recvBuffComp
#if FW_OBJECT_NAMES == 1
                    ("RBC")
#endif
;

Ref::SendBuffImpl sendBuffComp
#if FW_OBJECT_NAMES == 1
                    ("SBC")
#endif
;

#if FW_ENABLE_TEXT_LOGGING
Svc::ConsoleTextLoggerImpl textLogger
#if FW_OBJECT_NAMES == 1
                    ("TLOG")
#endif
;
#endif

Svc::ActiveLoggerImpl eventLogger
#if FW_OBJECT_NAMES == 1
                    ("ELOG")
#endif
;

Svc::LinuxTimeImpl linuxTime
#if FW_OBJECT_NAMES == 1
                    ("LTIME")
#endif
;

Svc::TlmChanImpl chanTlm
#if FW_OBJECT_NAMES == 1
                    ("TLM")
#endif
;

Svc::CommandDispatcherImpl cmdDisp
#if FW_OBJECT_NAMES == 1
                    ("CMDDISP")
#endif
;

Fw::MallocAllocator seqMallocator;
Svc::CmdSequencerComponentImpl cmdSeq
#if FW_OBJECT_NAMES == 1
                    ("CMDSEQ")
#endif
;

Svc::PrmDbImpl prmDb
#if FW_OBJECT_NAMES == 1
                    ("PRM","PrmDb.dat")
#else
                    ("PrmDb.dat")
#endif
;

Ref::PingReceiverComponentImpl pingRcvr
#if FW_OBJECT_NAMES == 1
                    ("PngRecv")
#endif
;

Svc::FileUplink fileUplink ("fileUplink");
Svc::FileDownlink fileDownlink ("fileDownlink", DOWNLINK_PACKET_SIZE);
Svc::BufferManager fileDownlinkBufferManager("fileDownlinkBufferManager", DOWNLINK_BUFFER_STORE_SIZE, DOWNLINK_BUFFER_QUEUE_SIZE);
Svc::BufferManager fileUplinkBufferManager("fileUplinkBufferManager", UPLINK_BUFFER_STORE_SIZE, UPLINK_BUFFER_QUEUE_SIZE);
Ref::SignalGen SG1("signalGen1");
Svc::HealthImpl health("health");

Ref::SignalGen SG2
#if FW_OBJECT_NAMES == 1
("signalGen2")
#endif
;

Ref::SignalGen SG3
#if FW_OBJECT_NAMES == 1
("signalGen3")
#endif
;

Ref::SignalGen SG4
#if FW_OBJECT_NAMES == 1
("signalGen4")
#endif
;

Ref::SignalGen SG5
#if FW_OBJECT_NAMES == 1
("signalGen5")
#endif
;

Svc::AssertFatalAdapterComponentImpl fatalAdapter
#if FW_OBJECT_NAMES == 1
("fatalAdapter")
#endif
;

Svc::FatalHandlerComponentImpl fatalHandler
#if FW_OBJECT_NAMES == 1
("fatalHandler")
#endif
;


#if FW_OBJECT_REGISTRATION == 1

void dumparch(void) {
    simpleReg.dump();
}

#if FW_OBJECT_NAMES == 1
void dumpobj(const char* objName) {
    simpleReg.dump(objName);
}
#endif

#endif

void constructApp(int port_number, char* hostname, char* targetname) {

    localTargetInit();

#if FW_PORT_TRACING
    Fw::PortBase::setTrace(false);
#endif    

    // Initialize rate group driver
    rateGroupDriverComp.init();

    // Initialize the rate groups
    rateGroup1Comp.init(10,0);
    
    rateGroup2Comp.init(10,1);
    
    rateGroup3Comp.init(10,2);

    // Initialize block driver
    blockDrv.init(10);

    // Send/Receive example hardware components
    recvBuffComp.init();
    sendBuffComp.init(10);

#if FW_ENABLE_TEXT_LOGGING
    textLogger.init();
#endif

    eventLogger.init(10,0);

    linuxTime.init(0);

    chanTlm.init(10,0);

    cmdDisp.init(20,0);

    cmdSeq.init(10,0);
    cmdSeq.allocateBuffer(0,seqMallocator,5*1024);

    prmDb.init(10,0);

    zmqRadio.init(100,1);

    fileUplink.init(30, 0);
    fileDownlink.init(30, 0);
    fileUplinkBufferManager.init(0);
    fileDownlinkBufferManager.init(1);
    SG1.init(10,0);
	SG2.init(10,1);
	SG3.init(10,2);
	SG4.init(10,3);
	SG5.init(10,4);
	fatalAdapter.init(0);
	fatalHandler.init(0);
	health.init(25,0);
	pingRcvr.init(10);
    // Connect rate groups to rate group driver
    constructRefArchitecture();

    /* Register commands */
    sendBuffComp.regCommands();
    recvBuffComp.regCommands();
    cmdSeq.regCommands();
    cmdDisp.regCommands();
    eventLogger.regCommands();
    prmDb.regCommands();
    fileDownlink.regCommands();
    SG1.regCommands();
    SG2.regCommands();
    SG3.regCommands();
    SG4.regCommands();
	SG5.regCommands();
	health.regCommands();
	pingRcvr.regCommands();

    // read parameters
    prmDb.readParamFile();
    recvBuffComp.loadParameters();
    sendBuffComp.loadParameters();

    // set health ping entries

    Svc::HealthImpl::PingEntry pingEntries[] = {
        {3,5,rateGroup1Comp.getObjName()}, // 0
        {3,5,rateGroup2Comp.getObjName()}, // 1
        {3,5,rateGroup3Comp.getObjName()}, // 2
        {3,5,cmdDisp.getObjName()}, // 3
        {3,5,eventLogger.getObjName()}, // 4
        {3,5,cmdSeq.getObjName()}, // 5
        {3,5,chanTlm.getObjName()}, // 6
        {3,5,fileUplink.getObjName()}, // 7
        {3,5,blockDrv.getObjName()}, // 8
        {3,5,fileDownlink.getObjName()}, // 9
        {3,5,pingRcvr.getObjName()}, // 10
    };

    // register ping table
    health.setPingEntries(pingEntries,FW_NUM_ARRAY_ELEMENTS(pingEntries),0x123);

    // Active component startup
    // start rate groups
    rateGroup1Comp.start(ACTIVE_COMP_1HZ_RG, 120,10 * 1024);
    rateGroup2Comp.start(ACTIVE_COMP_P5HZ_RG, 119,10 * 1024);
    rateGroup3Comp.start(ACTIVE_COMP_P25HZ_RG, 118,10 * 1024);
    // start driver
    blockDrv.start(ACTIVE_COMP_BLKDRV,140,10*1024);
    // start dispatcher
    cmdDisp.start(ACTIVE_COMP_CMD_DISP,101,10*1024);
    // start sequencer
    cmdSeq.start(ACTIVE_COMP_CMD_SEQ,100,10*1024);
    // start telemetry
    eventLogger.start(ACTIVE_COMP_LOGGER,98,10*1024);
    chanTlm.start(ACTIVE_COMP_TLM,97,10*1024);
    prmDb.start(ACTIVE_COMP_PRMDB,96,10*1024);

    fileDownlink.start(ACTIVE_COMP_FILE_DOWNLINK, 100, 10*1024);
    fileUplink.start(ACTIVE_COMP_FILE_UPLINK, 100, 10*1024);

    pingRcvr.start(ACTIVE_COMP_PING_RECEIVER, 100, 10*1024);

    zmqRadio.open(hostname, port_number, targetname);
    zmqRadio.start(ACTIVE_ZMQ_RADIO, 90, 20*1024);


#if FW_OBJECT_REGISTRATION == 1
    //simpleReg.dump();
#endif

}

//void run1cycle(void) {
//    // get timer to call rate group driver
//    Svc::TimerVal timer;
//    timer.take();
//    rateGroupDriverComp.get_CycleIn_InputPort(0)->invoke(timer);
//    Os::Task::TaskStatus delayStat = Os::Task::delay(1000);
//    FW_ASSERT(Os::Task::TASK_OK == delayStat,delayStat);
//}


void run1cycle(void) {
    // call interrupt to emulate a clock
    blockDrv.callIsr();
    Os::Task::delay(1000); //10Hz
}

void runcycles(NATIVE_INT_TYPE cycles) {
    if (cycles == -1) {
        while (true) {
            run1cycle();
        }
    }

    for (NATIVE_INT_TYPE cycle = 0; cycle < cycles; cycle++) {
        run1cycle();
    }

}

void exitTasks(void) {
    rateGroup1Comp.exit();
    rateGroup2Comp.exit();
    rateGroup3Comp.exit();
    blockDrv.exit();
    cmdDisp.exit();
    eventLogger.exit();
    chanTlm.exit();
    prmDb.exit();
    fileUplink.exit();
    fileDownlink.exit();
    cmdSeq.exit();
    zmqRadio.exit();
}

void print_usage() {
	(void) printf("Usage: ./Ref [options]\n"
                  "-p\tport_number         [ REQUIRED ]\n"
                  "-a\thostname/IP address [ REQUIRED ]\n"
                  "-n\ttargetname          [ REQUIRED ]\n\n");
}

#if defined TGT_OS_TYPE_LINUX || TGT_OS_TYPE_DARWIN

#include <signal.h>
#include <stdio.h>

volatile sig_atomic_t terminate = 0;

static void sighandler(int signum) {
	terminate = 1;
}

int main(int argc, char* argv[]) {
	U32 port_number;
	I32 option;
	char *hostname;
    char *targetname;
	port_number = 0;
	option = 0;
	hostname = NULL;

	while ((option = getopt(argc, argv, "h::p:n:a:")) != -1){
		switch(option) {
			case 'h':
				print_usage();
				return 0;
				break;
			case 'p':
				port_number = atoi(optarg);
				break;
			case 'a':
				hostname = optarg;
				break;
            case 'n':
                targetname = optarg;
                break;
			case '?':
				return 1;
			default:
				print_usage();
				return 1;
		}
	}

	(void) printf("Hit Ctrl-C to quit\n");

    if(hostname == NULL || port_number == NULL || targetname == NULL){
        print_usage();
        return 1;
    }


    printf("Address: %s", hostname);
    printf("Port: %d\n", port_number);
    printf("Target Name: %s\n", targetname);

    constructApp(port_number, hostname, targetname);
    //dumparch();

    signal(SIGINT,sighandler);
    signal(SIGTERM,sighandler);

    int cycle = 0;

    while (!terminate) {
//        (void) printf("Cycle %d\n",cycle);
        runcycles(1);
        cycle++;
    }

    // stop tasks
    exitTasks();
    // Give time for threads to exit
    (void) printf("Waiting for threads...\n");
    Os::Task::delay(1000);

    (void) printf("Exiting...\n");

    return 0;
}

#endif

#ifdef TGT_OS_TYPE_VXWORKS

#include "Fw/Types/VxWorks/VxWorksLogAssert.hpp"

extern "C" {
    void go(int portNum, char* hostname);
}

void cycleTask(void* arg) {
    runcycles(-1);
}

Os::Task cycleTaskObj;

Fw::VxWorksLogAssertHook logAssertHook;

void go(int portNum, char* hostname) {
    logAssertHook.registerHook();
    constructApp(portNum,hostname, targetname);
    // start thread cycling
    Fw::EightyCharString taskName("Cycler");
    if (cycleTaskObj.start(taskName,CYCLER_TASK,160, 10*1024,cycleTask,0) != Os::Task::TASK_OK) {
        printf("Failed to start cycler task!\n");
    }

    Os::Task::delay(10000);
}

#endif

#ifdef TGT_OS_TYPE_RTEMS

#include <stdio.h>
#include <rtems/rtems_config.h>


rtems_task Init (rtems_task_argument ignored) {

    (void) printf("Constructing Architecture\n");

    // *** Probably broken. Hasn't been tested in a few releases ***

    constructApp();

    int cycle = 0;

    while (cycle != 10) {
        Os::Task::delay(1000);
        (void) printf("Cycle %d\n",cycle);
        runcycles(1);
        cycle++;
    }

    // stop tasks
    rateGroup1KhzComp.exit();
    rateGroup100hzComp.exit();
    rateGroup1hzComp.exit();
    blockDrv.exit();

    // Give time for threads to exit
    (void) printf("Waiting for threads...\n");
    Os::Task::delay(1000);

    (void) printf("Exiting...\n");
    exit(0);
}

#endif
