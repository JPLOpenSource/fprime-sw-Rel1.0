# COSMOS Autocoder Tool Documentation

This tool found in Autocoders/bin at cosmosgen.py autocodes all of the configuration files required by the [Ball Aerospace COSMOS UI](http://cosmosrb.com/) in order to add a new deployment (called target within COSMOS) specified in a Topology XML file.

## 1. Overview

COSMOS is a "User Interface for Command and Control of Embedded Systems" made in Ruby that lets users send commands / view telemetry within special customizable COSMOS tools configured in text files using COSMOS syntax documented [here](http://cosmosrb.com/docs/home/).  Some of these tools include a cmd\_tlm server application that can handle server, client, serial, UDP, and potentially any other format through Ruby [scripts](http://cosmosrb.com/docs/scripting/), a data\_viewer application that displays a continuous stream of telemetry text data, and a tlm\_viewer application that has users create GUI [screens](http://cosmosrb.com/docs/screens/) that display telemetry data statically.

Our tool uses [Cheetah templates](https://pythonhosted.org/Cheetah/) found [here](../Autocoders/src/utils/cosmos/templates) in order to Autocode the COSMOS configuration files.  The entire COSMOS/config/targets/TARGET\_NAME/ directory is created by the autocoder, however there are also a few other files within the COSMOS/config directory/ that the autocoder will append to if it already exists.

To **delete** a target, run the autocoder with -r TARGET_NAME, and it will remove it from all the autocoded files.

## 2. Installing the Tool

### 2.1 Mac

The COSMOS Autocoder Tool requires FPrime and COSMOS to be installed along with their unique dependencies.

Instructions for installing FPrime can be found in the [User Guide](../docs/UsersGuide/FprimeUserGuide.pdf).

Instructions for installing COSMOS can be found in the [Installation Guide](INSTALL\_NOTES.txt) in the COSMOS directory.

Once both of these are fully installed, run "cosmos demo FILE\_NAME" inside any directory to generate a working COSMOS environment.  To add your Topology to that environment run the run\_cosmosgen.sh script in Autocoders/bin with "-b COSMOS\_PATHNAME" and the path to your Topology.xml file as an argument.  In addition, if you would like to have the script generate into the COSMOS directory that comes packaged inside of this repository, simply run the script with only the path to your Topology.xml file.

Tools are accessed in the tools directory on the top of your COSMOS directory.  All files within Autocoders/src/utils/cosmos must be present in order for the script to function properly.

### 2.2 Linux

In Progress

## 3. Running the Tool

To use the tool, run the run\_cosmosgen.sh script from the command line with the directory for the Topology XML file as the only argument.  In order to update the Cheetah templates used when generating the COSMOS configuration files, there is a script in Autocoders/src/utils/cosmos/templates called compile\_templates.sh that takes no arguments.

## 4. Tool Inputs and Outputs

## 4.1 Inputs

The only command line argument that the tool takes is the location of Topology XML file.  It should start at the directory of the command line and look like "../../Ref/Top/RefTopologyAppAi.xml"

As the Topology XML files only contain information regarding command and telemetry packets, **all changes to communication protocol and shared command/telemetry packet items should be manually entered into the CosmosUtil module in the util directory and into the command and telemetry header files generated within the deployment's COSMOS cmd_tlm directory respectively**.  The default for these protocols and headers are the fields for the Fprime Reference Application.

In addition to adding targets based on Topology XML files, the tool is able to remove targets via the command-line option "-r TARGET_NAME".  The SYSTEM target should never be deleted, because COSMOS uses it in the background for all other targets.

## 4.2 Outputs

The tool outputs COSMOS config text files to the directory set via command-line (default: fprime-sw/COSMOS).  These text files are generated via Cheetah templates in the Autocoders/src/utils/cosmos/templates directory.  Cosmos config files are documented [here](http://cosmosrb.com/docs/home/).  The tool is also set to generate the 3 Ruby scripts documented in section 5 below into the lib directory of Cosmos if they are not already present.

### Generated text files
|Name|Description
|---|---|
|\_ref\_cmd\_hdr.txt|Contains all shared header fields for commands|
|\_ref\_tlm\_chn\_hdr.txt|Contains all shared header fields for channels|
|\_ref\_tlm\_evr\_hdr.txt|Contains all shared header fields for events|
|\_user\_dataviewers.txt|Contains room for users to input their own data_viewer definition files|
|channels.txt|Contains COSMOS screen definition for the target's Channel display for the tlm_viewer application|
|cmd\_tlm\_server.txt|Contains links to the other cmd\_tlm\_server.txt files found within each target's own directory|
|cmd\_tlm\_server.txt|Contains interface and protocol definitions for each target i.e. what ports for r/w, sync definition|
|data\_viewer.txt|Contains links to the other data\viewer.txt files found within each target's own directory|
|data\_viewer.txt|Contains definition for which EVR's to display in the EVR display for the data_viewer application|
|system.txt|Contains declarations for all targets|
|system.txt|Contains target declarations for all targets|
|target.txt|Contains include statements for all the necessary generated ruby scripts|
|tlm\_viewer.txt|Contains links to the other screen definition files found within each target's own directory|
|Channel text files|Contains channel telemetry definitions for each channel in the deployment|
|Command text files|Contains command telemetry definitions for each command in the deployment|
|Event text files|Contains event telemetry definitions for each event in the deployment|



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

#### 5.1.3 The Autocoders/src/utils/cosmos/util Directory
|Name|Description|Link
|---|---|---|
|CheetahUtil.py|Contains constants and methods that affect the way data is outputted to the Cheetah templates|[.py](../Autocoders/src/utils/cosmos/models/CheetahUtil.py)|
|CosmosUtil.py|Contains all the hardcoded data regarding interfaces and protocols i.e. port number, header-bit-length|[.py](../Autocoders/src/utils/cosmos/models/CosmosUtil.py)|

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
|RubyWriter.py|Class that prints out user-input files for applications|[.py](../Autocoders/bin/writers/RubyWriter.py) [.tmpl](../Autocoders/src/utils/cosmos/templates/ruby\_evr\_dump\_component.tmpl) [.tpml](../Autocoders/src/utils/cosmos/templates/ruby\_multi\_string\_tlm\_item\_conversion.tmpl) [.tmpl](../Autocoders/src/utils/cosmos/templates/ruby\_ref\_protocol.tmpl)|
|ServerWriter.py|Class that writes the server config file|[.py](../Autocoders/bin/writers/ServerWriter.py) [docs](http://cosmosrb.com/docs/interfaces/) [.tmpl](../Autocoders/src/utils/cosmos/templates/cosmos\_server.tmpl)|
|TargetWriter.py|Class that writes the target config file|[.py](../Autocoders/bin/writers/TargetWriter.py) [docs](http://cosmosrb.com/docs/system/) [.tmpl](../Autocoders/src/utils/cosmos/templates/target.tmpl)|

### 5.2 Helper Ruby Scripts
|Name|Description|Link
|---|---|---|
|evr\_dump\_component.rb|Plain text writing protocol that specifies how text should be written in the data_viewer application|[.rb](../COSMOS/lib/evr\_dump\_component.rb)|
|multi\_string\_item\_conversion.rb|Ruby script that is used in event telemetry to allow COSMOS to handle multiple strings by pre-specifying all packet items in a single BLOCK-type item and then parsing out their values within this script rather than in COSMOS itself|[.rb](../COSMOS/lib/multi\_string\_item\_conversion.rb)|
|ref\_protocol.rb|Optional helper script for FPrime ref app that bypasses an error message that gets sent out when COSMOS doesn't recognize the first 13 bits the ref app sends|[.rb](../COSMOS/lib/ref\_protocol.rb)|
