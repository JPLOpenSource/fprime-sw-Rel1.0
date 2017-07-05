# fprime-zmq

This repository is meant to be used as a sub-repository under an F' derived repository. It adds ZeroMQ:

http://zeromq.org

The `zmq` directory has the ported ZMQ source code and license files.

## Components

The following components are provided:

|Component|Description|Status|
|---|---|---|
|`zmq-router`|A generic router with serialize input/ouput ports for sending port invocations to other nodes via ZMQ.|In progress, doesn't work yet|
|`zmq-pub`|A component with serialize input ports for publishing port calls.|Not started|
|`zmq-sub`|A component with serialize output ports for subscribing to port calls.|Not started|
|`zmq-radio`|A component with uplink/downlink ports that communicate via ZMQ with a ground system|Not started|

See the component SDD files in their respective `docs` subdirectories.

## Modifications to your repo:

The following modifications should be made to the build configuration files to allow the code to compile:

`<root>/mk/configs/compiler/include_common.mk`

Add:

`-I$(BUILD_ROOT)/fprime-zmq/zmq/include`

`<root>/mk/configs/compiler/defines_common.mk`

Add:

`-DZMQ_BUILD_DRAFT_API` if you wish to use the ZMQ draft API. (Needed for `zmq_router`)



