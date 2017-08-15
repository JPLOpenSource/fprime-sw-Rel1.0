
# ZmqRadio Component

## 1. Introduction

The ZmqRadio is an active component that provides an interface to the 
ZeroMQ based GSE server. 

The component takes input from a `Fw::Com` and `Fw:BufferSend` port.
These inputs are serviced by the downlinkPort_handler and 
filedownlinkbuffersendin_handler, respectively. 

An `Os::Task` listener thread, groundSubscriptionListener, runs in parallel with the ZmqRadio's 
main thread. This listener thread blocks and listens for packets coming
from the ground system. 

In order to support persistent reconnection attempts and component stability,
the ZmqRadio maintains two internal states:

- ZMQ_RADIO_DISCONNECTED
- ZMQ_RADIO_CONNECTED

The ZmqRadio's internal state controls the input handlers to keep message queues 
from backing up. The internal state also facilitates persistent reconnection
attempts. 


## 2. Requirements
Requirement | Description | Verification Method
----------- | ----------- | -------------------
1 | All input handlers shall drop incoming messages while in ZMQ_RADIO_DISCONNECTED. |
2 | The 'Zmq::ZmqRadio::groundSubscriptionListener' shall be idle while in ZMQ_RADIO_DISCONNECTED. |
3 | All ZMQ resources shall be released upon transitioning from ZMQ_RADIO_CONNECTED to\
ZMQ_RADIO_DISCONNECTED. | 
4 | The 'Zmq::ZmqRadio' component shall transition to ZMQ_RADIO_DISCONNECTED state if any ZMQ is experienced. |
5 | ZMQ shall be configured with the options below. |

ZMQ Option | Description | ZmqRadio Value 
---------- | ----------- | --------------
ZMQ_LINGER | How long to keep socket alive after a socket close call. | 0 seconds
ZMQ_RCVTIMEO | How long before a zmq_msg_recv call returns an EAGAIN error. | 200 ms 
ZMQ_SNDTIMEO | How long before a zmq_msg_send call returns an EAGAIN error. | 200 ms

## 3. Functional Description

### 3.1 downlinkPort_handler 

### 3.2 filedownlinkbuffersendin_handler 

### 3.3 groundSubscriptionListener 

### 3.4 transitionConnected

### 3.5 transitionDisconnected
 
