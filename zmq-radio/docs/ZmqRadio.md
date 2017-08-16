<title>ZmqRadio Component Dictionary</title>
# ZmqRadio Component Dictionary


## Telemetry Channel List

|Channel Name|ID|Type|Description|
|---|---|---|---|
|ZR_PacketsSent|0 (0x0)|U32|Number of packets sent|
|ZR_NumDisconnects|1 (0x1)|U32|Number of times ZmqRadio has transitioned to disconnected state|
|ZR_NumConnects|2 (0x2)|U32|Number of times ZmqRadio has transitioned to connected state|
|ZR_NumRecvTimeouts|3 (0x3)|U32|Number of times ZmqRadio has timed out|
|ZR_PktsSent|4 (0x4)|U32|Number of packets sent|
|ZR_PktsRecv|5 (0x5)|U32|Number of packets received|

## Event List

|Event Name|ID|Description|Arg Name|Arg Type|Arg Size|Description
|---|---|---|---|---|---|---|
|ZR_ContextError|1 (0x1)|ZmqRadio context open error| | | | |
| | | |error|Fw::LogStringArg&|80||    
|ZR_SocketError|2 (0x2)|ZmqRadio socket error| | | | |
| | | |error|Fw::LogStringArg&|80||    
|ZR_BindError|3 (0x3)|ZmqRadio bind error| | | | |
| | | |error|Fw::LogStringArg&|80||    
|ZR_SendError|4 (0x4)|ZmqRadio send error| | | | |
| | | |error|Fw::LogStringArg&|80||    
|ZR_Disconnection|5 (0x5)|ZmqRadio component disconneted| | | | |
|ZR_Connection|6 (0x6)|ZmqRadio component connected to server| | | | |
|ZR_RecvTimeout|7 (0x7)|ZmqRadio component connected to server| | | | |
