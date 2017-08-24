# Client - OpenMCT
 
## 1. Introduction
User Guide is [here](#User Guide)

The `client-openmct` module is used to interface with targets using a [Node.js](https://nodejs.org) server and [Open Source Mission Control Software](https://nasa.github.io/openmct/) developed by AMES Research center. A computer sets up an instance of the Node.js server while the usual TCP server and targets are running. Clients connect to the server through their web browser, preferebly [Google Chrome](https://www.google.com/chrome/)

![OpenMCT Client] (res/img/PlotSS1.png)

## 3. Design

### 3.2 Protocols
The Node.js server serializes commands from the client to the TCP server and deserializes channel and event telemetry from a binary buffer to a datum object that OpenMCT can read.

#### 3.2.1 Serialization
Channel Telemetry

|              | Packet Size | Packet Descriptor | Channel ID | Time Base | Time Context | Seconds | Microseconds | Channel Value  |
| :----------- | :---------: | :---------------: | :--------: | :-------: | :----------: | :-----: | :----------: | :------------: |
| Size (bytes) | 4           | 4                 | 4          | 2         | 1            | 4       | 4            | Rest           |
| Type         | U32         | U32               | U32        | U16       | U8           | U32     | U32          | Use dictionary |
| Description  | Size starting at the beginning of Packet Descriptor to the end of packet. | '1' signifying channels | Used to access channel attributes in dictionary | <!--Time Base ??-->| <!--Time Context ??--> | Epoch time datum was sent from target | Epoch microseconds of datum timestamp | Value of channel. Use dictionary to figure out type, enum, or string format |


### 3.3 Context

![Context Diagram](res/img/WebAppContextDiagram.png)



## <a name="User Guide"></a>4. User Guide

```
npm install
npm start
```