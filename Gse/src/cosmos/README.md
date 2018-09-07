COSMOS GSE Utilities
====================

This directory contains the COSMOS implementation of `gse_api.py`, which allows a
developer to send commands and receive events and telemetry from a COSMOS telemetry
server connected to an F' target. The GseApi remains largely unchanged,
with the intention that any existing integration scripts using `utils.gse_api.py`
will function exactly the same way, with the simple substitution of `cosmos.gse_api`.
However, the implementation has been entirely decoupled from the generated dictionaries,
instead loading all necessary telemetry and command metadata from the COSMOS server.

NOTE: The only change to the existing API is that the constructor of GseApi now
accepts an optional 'deployment' parameter. Every HTTP request to the COSMOS server must
specify a target, so the GseApi uses the following procedure to determine the
target name:
1. 'deployment' parameter (recommended): Most concise, direct method. If 'deployment'
is specified in the constructor, GseApi uses this as the target name. Should be
used for any future development with this API.
2. 'generated_path' parameter: Included for backward compatibility with existing GseApi.
Parses the target name from this path, assuming the name of the last directory in the path is the target name.
3. 'generated_path' configuration: Included for backward compatibility. Same as above,
but gets value of 'generated_path' from .ini configuration.
4. COSMOS API: Gets a list of available targets from the COSMOS server, and uses
the first one which is not COSMOS's internal 'SYSTEM' target. This is intended as
a fallback, as this is essentially a guess if COSMOS has been configured with more
than one valid target.


Installation
------------
To use these utilities you will need a working python 2.7 installation. The recommended python environment setup is outlined [here](https://github.jpl.nasa.gov/ASTERIA/FSW/blob/master/Gse/README.md).

Using the GSE API
-----------------
To best see the methods available in the GSE API, install [pydoc](https://docs.python.org/2/library/pydoc.html) and run:

    pydoc gse_api

## COSMOS HTTP API
The COSMOS telemetry server provides an [HTTP API](https://cosmosrb.com/docs/json_api/) which can be used to access realtime telemetry, send commands, and load telemetry metadata, among other things. This section provides a quick overview of the API, and how a high-level description of how it is used in the COSMOS version of GseApi.py.

The COSMOS telemetry server listens for HTTP requests on a dedicated port, 7777
by default. All HTTP requests are POSTed to this address, with JSON data formatted as a [JSON-RPC request](https://www.jsonrpc.org/specification) as follows:
```
{
  'jsonrpc': 2.0,
  'method': <Method Name>
  'params': <Method Parameters>
  'id': 0
}
```
where 'id' can be any alphanumeric string used to identify the request. The full
list of API methods and their parameters can be found in the cmd_tlm_server source
code
[here](https://github.com/BallAerospace/COSMOS/blob/master/lib/cosmos/tools/cmd_tlm_server/api.rb).

### GSE Classes
This section describes the contents of this directory, which allow interaction
with the COSMOS API while abstracting out the handling of HTTP requests and responses.

| Name | Description |
| ---- | ----------- |
| cosmos_command_loader.py | Loads command names, opcodes, and arguments, and exposes them as Python dictionaries. |
| cosmos_command_sender.py | Sends commands using the COSMOS commanding API. |
| cosmos_http_request.py | Simple abstraction of COSMOS HTTP requests. |
| cosmos_telem_loader.py | Loads event and telemetry names and id's, and exposes them as Python dictionaries. |
| cosmos_telem_queue.py | Creates a telemetry queue on the COSMOS server and retrieves data from it. |
| gse_api.py | COSMOS version of the generic GSE API used to build integration tests. Contains a main() method with example usage of each API method.|
| bin/ | Example test scripts duplicated from `utils/`, included to test backward compatibility |

### Usage in COSMOS GseApi
The GSE API first constructs a COSMOSTelemLoader, which makes several HTTP queries
to construct maps of events and channels to their ids:
1. Calls `get_tlm_list`, which returns a list of all telemetry known to COSMOS for
the deployment provided as argument.
2. Calls `get_telem_details`, with arguments [[DEPLOYMENT_NAME, TELEM_NAME, "DESC"] ... ],
which gets a list of attributes for the "DESC" field of a each telemetry item.
"id_value" attribute contains the descriptor for each telemetry point, so they
can be separated into channels and EVRs.
3. Calls `get_telem_details` again with arguments [[DEPLOYMENT_NAME, TELEM_NAME "EVR_ID"] ...]
and [[DEPLOYMENT_NAME, TELEM_NAME "CHANNEL_ID"] ...] for each EVR and channel,
respectively, and again access the "id_value" attribute, which is the id of the
EVR or channel.

It then constructs two COSMOSTelemQueues, one for channels and one for EVRs, which
operate as follows:
1. The COSMOSTelemQueue is constructed with a list of telemetry names. GseApi first
loads all available telemetry as described above, then instantiates a queue with
the list of EVR names, and one with the list of channel names.
2. COSMOSTelemQueue calls `subscribe_packet_data` with arguments [[DEPLOYMENT_NAME, TELEM_NAME] ...]
for each telemetry item in the list it was instantiated with. This sets up a queue
on the COSMOS telemetry server which will be populated with realtime telemetry. COSMOS
assigns this queue a unique id, which is returned in the reply to this request.
3.  When COSMOSTelemQueue's get_next_value() method is called, it sends a `get_packet_data`
request with arguments of [queue_id, non-blocking], where queue_id is the unique
id of the queue on the COSMOS server, and non-blocking indicates whether this
method should block until telemetry is available, or send a 'queue empty' reply
if no telemetry is available.
4. If the queue exceeds a certain threshold of backlogged telemetry, the server
may automatically destroy it. In this case, requests to `get_packet_data` will
return errors.

Finally, it constructs a COSMOSCommandSender, which in turn constructs a COSMOSCommandLoader, which does the following:
1. Gets a list of all available commands with method `get_cmd_list` and argument [DEPLOYMENT_NAME].
2. For each command, calls `get_cmd_param_list` with arguments [DEPLOYMENT_NAME, COMMAND_NAME],
which returns a description of each command argument, including their opcodes, and
constructs maps of name->opcode, opcode->name, and name->arguments.

The COSMOSCommandSender has a send() method, which takes as arguments the command
name and parameters. It sends the command on to COSMOS using the `cmd` method, which
takes as argument a string of the form 'TARGET COMMAND with ARG1_NAME ARG1_VALUE, ... , ARGN_NAME, ARGN_VALUE',
which is constructed by the COSMOSCommandSender instance.
