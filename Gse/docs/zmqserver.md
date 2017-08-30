
# FPrime GSE ZmqServer

## 1. Introduction

The GSE ZmqServer is a redesign of the legacy ThreadedTCPServer. 
The ZmqServer reqires flight and ground clients to use the Zmq library.
<a href="http://zeromq.org/">http://zeromq.org</a>

The ZmqServer offers the following features:
- Runtime customizable many-many communication implemented using Pub/Sub architecture
- Pluggable protocol translators

This document first covers these features and the use of the server.
Then implementation details are discussed. 


## 2. Use
The server is controlled and monitored through it's `Command Port`. The `Command Port` is the
common connection point for all flight and ground clients. Clients use this port for registration
and server introspection. 

One process is created 

A list of command definitions can be seen in `server/ServerUtils/server_config.py`.

### ZmqServer Commands
Commands are delimited as Zmq Frames. Examples on sending commands are shown below the tables.
Wrapper to these commands are available in the GSE Api.


Command | Description | Usage | Server Response
------- | ----------- | ----- | ---------------
ServerConfig.REG_CMD | Register client to the server. Server allocates a publish, subscribe sockets for the client and return the port numbers in the response. | ['REG' <client_type> <protocol>] | [<status> <server_pub_port> <server_sub_port>]
ServerConfig.SUB_CMD | Subscribe a client to one or more other clients | ['SUB' <client_name> <client_type> <pub_client_1>...<pub_client_n> ] | [<status>]
ServerConfig.USUB_CMD | Unsubscribe a client from one or more other clients | ['USUB' <client_name> <client_type> <pub_client_1>...<pub_client_n>] | [<status>]
ServerConfig.LIST_CMD | Request a list of Flight and Ground client subscriptions | ['LIST'] | [<pickled_client_sub_dict>]

#### Arguments

Arg | Description | Value
--- | ----------- | -----
<client_type> | Flight or ground client | `ServerConfig.FLIGHT_TYPE` or `ServerConfig.GROUND_TYPE`
<protocol> | Any implemented protocol translator class residing in server.AdapterLayer.plugins | The name of the protocol
<pub_client> | The name of a publishing client to subscribe to
<pickeled_client_sub_dict> | A pickled dictionary contaning subscription information about all Flight and Ground clients

#### Registration example
##### Python

##### C++
#### Subscription example

#### List example


## 2. Requirements
Requirement | Description | Verification Method
----------- | ----------- | -------------------
1 | All input handlers shall drop incoming messages while in `ZMQ_RADIO_DISCONNECTED`. | 
2 | The 'Zmq::ZmqRadio::subscriptionTask' shall be idle while in `ZMQ_RADIO_DISCONNECTED`. |
3 | All ZMQ resources shall be released upon transitioning from `ZMQ_RADIO_CONNECTED` to `ZMQ_RADIO_DISCONNECTED`. | 
4 | `Zmq::ZmqRadio::State::transitionDisconnected` shall be called if, apart from EAGAIN, a ZMQ error is experienced anywhere. |
5 | `Zmq::ZmqRadio::State::transitionDisconnected` shall be called after `ZMQ_RADIO_SNDHWM` number of failed socket sends.
6 | `Zmq::ZmqRadio::State::transitionConnected` shall be called if `Zmq::ZmqRadio` successfully registers to the server. | 
7 | ZMQ library shall be configured with the options below. |
8 | The `Zmq::ZmqRadio` component shall be configured with the options below. |

ZMQ Option | Description |  Value 
---------- | ----------- | --------------
`ZMQ_LINGER` | How long to keep socket alive after a socket close call. | 0 seconds
`ZMQ_RCVTIMEO` | How long before a `zmq_msg_recv` call returns an EAGAIN error. | 200 ms 
`ZMQ_SNDTIMEO` | How long before a `zmq_msg_send` call returns an EAGAIN error. | 200 ms


`Zmq::ZmqRadio` Option | Description |  Value 
---------- | ----------- | --------------
`ZMQ_RADIO_NUM_RECV_TRIES` | Number of times the component retries receiving an uplinked packet. | 5
`ZMQ_RADIO_SNDHWM` | Maximum number of outbound packets queued until transition to `ZMQ_RADIO_DISCONNECTED` | 5

## 3. Design

### 3.1 Context

#### 3.1.1 Component Diagram

![ZmqRadioComponentDiagram](img/ZmqRadioBDD.png "ZmqRadioComponent") 

#### 3.1.2 State Diagram

![ZmqRadioStateDiagram](img/ZmqRadioState.png "ZmqRadioState") 

## 4. Functional Description

### 4.1 downlinkPort_handler 
If `ZMQ_RADIO_CONNECTED`:     This handler invokes the helper function 'zmqSocketWriteComBuffer'.<br>
If `ZMQ_RADIO_DISCONNECTED`:  No action.

### 4.2 filedownlinkbuffersendin_handler 
If `ZMQ_RADIO_CONNECTED`:     This handler invokes the helper function 'zmqSocketWriteFwBuffer'.<br>
If `ZMQ_RADIO_DISCONNECTED`:  No action.

### 4.3 groundSubscriptionListener 
If `ZMQ_RADIO_CONNECTED`:     This handler polls for uplinked packets and delivers the packets to their
                            destination component. <br> 
If `ZMQ_RADIO_DISCONNECTED`:  No action.

### 4.4 transitionConnected
If `ZMQ_RADIO_CONNECTED`:     No action. <br>                           
If `ZMQ_RADIO_DISCONNECTED`:  Set state to `ZMQ_RADIO_CONNECTED` 

### 4.5 transitionDisconnected
If `ZMQ_RADIO_CONNECTED`:     Set state to `ZMQ_RADIO_DISCONNECTED` and release ZMQ resources. <br> 
If `ZMQ_RADIO_DISCONNECTED`:  No action. 

### 4.6 reconnect_handler
Is connected to a 1Hz rategroup for persistent reconnection attempts.
If `ZMQ_RADIO_CONNECTED`:     No action. <br> 
If `ZMQ_RADIO_DISCONNECTED`:  Attempts connection and registration with the server.


## Telemetry Channel List
ZR_NumDisconnects
ZR_NumConnects
ZR_NumDisconnectRetries
ZR_PktsSent
ZR_PktsRecv

## Event List
ZR_ContextError
ZR_SocketError
ZR_BindError
ZR_Disconnection
ZR_Connection
ZR_SendError
ZR_ReceiveError
