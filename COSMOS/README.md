# COSMOS Autocoder Tool Documentation

This tool found in Autocoders/bin at cosmosgen.py autocodes all of the configuration files required by the [Ball Aerospace COSMOS UI](http://cosmosrb.com/) in order to add a new deployment (called target within COSMOS) specified in a Topology XML file.

## 1. Overview

COSMOS is a "User Interface for Command and Control of Embedded Systems" made in Ruby that lets users send commands / view telemetry within special customizable COSMOS tools configured in text files using COSMOS syntax documented [here](http://cosmosrb.com/docs/home/).  Some of these tools include a cmd\_tlm server application that can handle server, client, serial, UDP, and potentially any other format through Ruby [scripts](http://cosmosrb.com/docs/scripting/), a data\_viewer application that displays a continuous stream of telemetry text data, and a tlm_viewer application that has users create GUI [screens](http://cosmosrb.com/docs/screens/) that display telemetry data statically.

Our tool uses [Cheetah templates](https://pythonhosted.org/Cheetah/) found [here](../Autocoders/src/utils/cosmos/templates) in order to Autocode the COSMOS configuration files.  The entire COSMOS/config/targets/TARGET_NAME/ directory is created by the autocoder, however there are also a few other files within the COSMOS/config directory/ that the autocoder will append to if it already exists.

To **delete** a target, run the autocoder with -r TARGET_NAME, and it will remove it from all the autocoded files.

## 2. Installing the Tool

### 2.1 Mac



### 2.2 Linux

In Progress

## 3. Running the Tool

To use the tool, run the run\_cosmosgen.sh script from the command line with the directory for the Topology XML file as the only argument.  In order to update the Cheetah templates used when generating the COSMOS configuration files, there is a script in Autocoders/src/utils/cosmos/templates called compile\_templates.sh that takes no arguments.

## 4. Tool Inputs and Outputs

## 5. The Classes

Classes within the tool are broken down into lowest-level model and writer classes that represent the command and telemetry data and that do the actual file writing, mid-level parser and generator classes that create and utilize the model and writer classes, and one highest-level cosmosgen.py class that instantiates the parser and generator classes.  All cheetah templates are found in the Autocoders/utils/cosmos/templates directory and all Ruby scripts are found in the COSMOS/lib directory.

### 5.1 The Python Autocoder

#### 5.1.1 The Autocoders/bin Directory
|Name|Description|Link
|---|---|---|
|cosmosgen.py|Class containing main method as well as all command line interaction|[.py](../Autocoders/bin/cosmosgen.py)|

#### 5.1.2 The Autocoders/src/utils/cosmos Directory
|Name|Description|Link
|---|---|---|
|CosmosGenerator.py|Class that takes Writer class instances and calls their write() methods to generate COSMOS config files|[.py](../Autocoders/src/utils/cosmos/CosmosGenerator.py)|
|CosmosTopParser.py|Class that takes an XML Parser instance and organizes its cmd and tlm data into COSMOS model classes for ease of Cheetah templating|[.py](../Autocoders/src/utils/cosmos/CosmosTopParser.py)|

#### 5.1.3 The Autocoders/src/utils/cosmos/models Directory
|Name|Description|Link
|---|---|---|
|BaseCosmosObject.py|Base class containing all shared data between Channels, Commands, and Events|[.py](../Autocoders/src/utils/cosmos/models/BaseCosmosObject.py)|
|CosmosChannel.py|Class representing a telemetry channel that encapsulates all the data it needs in the Cheetah templates|[.py](../Autocoders/src/utils/cosmos/models/CosmosChannel.py)|
|CosmosCommand.py|Class representing a telemetry command that encapsulates all the data it needs in the Cheetah templates|[.py](../Autocoders/src/utils/cosmos/models/CosmosCommand.py)|
|CosmosEvent.py|Class representing a telemetry event that encapsulates all the data it needs in the Cheetah templates|[.py](../Autocoders/src/utils/cosmos/models/CosmosEvent.py)|

#### 5.1.4 The Autocoders/src/utils/cosmos/writers Directory
|Name|Description|Link
|---|---|---|
|AbstractCosmosWriter.py|Abstract class containing the definition of the write() method shared by all other writer classes|[.py](../Autocoders/src/utils/cosmos/writers/AbstractCosmosWriter.py)|
|BaseConfigWriter.py|Base class encapsulating all data shared between config files that must have lines appended to and removed rather than just having all its contents created new every time the autocoding tool is run|[.py](../Autocoders/src/utils/cosmos/writers/BaseConfigWriter.py)|
|ChannelScreenWriter.py|Class that writes the channel screen config file for the tlm\_viewer application|[.py](../Autocoders/bin/writers/ChannelScreenWriter.py) [docs](http://cosmosrb.com/docs/screens/) [.tmpl](../Autocoders/src/utils/cosmos/templates/channel\_screen.tmpl)|
|ChannelWriter.py|Class that writes the channel config file for the cmd\_tlm\_server application|[.py](../Autocoders/bin/writers/ChannelWriter.py) [docs](http://cosmosrb.com/docs/telemetry/) [.tmpl](../Autocoders/src/utils/cosmos/templates/channel.tmpl)|
|CommandWriter.py|Class that writes the command config file for the cmd\_tlm\_server application|[.py](../Autocoders/bin/writers/CommandWriter.py) [docs](http://cosmosrb.com/docs/command/) [.tmpl](../Autocoders/src/utils/cosmos/templates/command.tmpl)|
|ConfigDataViewerWriter.py|Class that writes the data\_viewer tool config file|[.py](../Autocoders/bin/writers/ConfigDataViewerWriter.py) [docs](http://cosmosrb.com/docs/data_viewer/) [.tmpl](../Autocoders/src/utils/cosmos/templates/data\_viewer\_config.tmpl)|
|ConfigServerWriter.py|Class that writes the cmd\_tlm\_server tool config file|[.py](../Autocoders/bin/writers/ConfigServerWriter.py) [docs](http://cosmosrb.com/docs/interfaces/) [.tmpl](../Autocoders/src/utils/cosmos/templates/server\_config.tmpl)|
|ConfigSystemWriter.py|Class that writes the system tool config file|[.py](../Autocoders/bin/writers/ConfigSystemWriter.py) [docs](http://cosmosrb.com/docs/system/) [.tmpl](../Autocoders/src/utils/cosmos/templates/system.tmpl)|
|ConfigTlmViewerWriter.py|Class that writes the tlm\_viewer tool config file|[.py](../Autocoders/bin/writers/ConfigTlmViewerWriter.py) [docs](http://cosmosrb.com/docs/tlm_viewer/) [.tmpl](../Autocoders/src/utils/cosmos/templates/tlm\_viewer\_config.tmpl)|
|DataViewerWriter.py|Class that writes the data\_viewer config file for the data\_viewer application|[.py](../Autocoders/bin/writers/DataViewerWriter.py) [docs](http://cosmosrb.com/docs/data_viewer/) [.tmpl](../Autocoders/src/utils/cosmos/templates/data\_viewer.tmpl)|
|EventWriter.py|Class that writes the event config file for the cmd\_tlm\_server application|[.py](../Autocoders/bin/writers/EventWriter.py) [docs](http://cosmosrb.com/docs/telemetry/) [.tmpl](../Autocoders/src/utils/cosmos/templates/event.tmpl)|
|PartialWriter.py|Class that prints out user-input files for applications|[.py](../Autocoders/bin/writers/PartialWriter.py) [.tmpl](../Autocoders/src/utils/cosmos/templates/channel\_partial.tmpl) [.tmpl](../Autocoders/src/utils/cosmos/templates/command\_partial.tmpl) [.tmpl](../Autocoders/src/utils/cosmos/templates/data\_viewer\_partial.tmpl) [.tmpl](../Autocoders/src/utils/cosmos/templates/event\_partial.tmpl)|
|ServerWriter.py|Class that writes the server config file|[.py](../Autocoders/bin/writers/ServerWriter.py) [docs](http://cosmosrb.com/docs/interfaces/) [.tmpl](../Autocoders/src/utils/cosmos/templates/cosmos\_server.tmpl)|
|TargetWriter.py|Class that writes the target config file|[.py](../Autocoders/bin/writers/TargetWriter.py) [docs](http://cosmosrb.com/docs/system/) [.tmpl](../Autocoders/src/utils/cosmos/templates/target.tmpl)|

### 5.2 Helper Ruby Scripts
|Name|Description|Link
|---|---|---|
|multi\_string\_item\_conversion.rb|Ruby script that is used in event telemetry to allow COSMOS to handle multiple strings by pre-specifying all packet items in a single BLOCK-type item and then parsing out their values within this script rather than in COSMOS itself|[.rb](../COSMOS/lib/multi\_string\_item\_conversion.rb)|
|ref\_protocol.rb|Optional helper script for FPrime ref app that bypasses an error message that gets sent out when COSMOS doesn't recognize the first 13 bits the ref app sends|[.rb](../COSMOS/lib/ref\_protocol.rb)|
