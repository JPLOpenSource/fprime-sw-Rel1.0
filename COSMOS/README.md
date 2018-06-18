# COSMOS Autocoder Tool Documentation

This tool found in Autocoders/bin at cosmosgen.py autocodes all of the configuration files required by the [Ball Aerospace COSMOS UI](http://cosmosrb.com/) in order to add a new deployment via its Topology XML file.

##1. COSMOS Overview

##2. Installing the Tool

###2.1 Mac

###2.2 Linux

###2.3 Windows

##3. Running the Tool

To use the tool, run the run\_cosmosgen.sh script from the command line with the directory for the Topology XML file as the only argument.  In order to update the Cheetah templates used when generating the COSMOS configuration files, there is a script in Autocoders/src/utils/cosmos/templates called compile\_templates.sh that takes no arguments.

##4. The Classes

|Name|Description|Link
|---|---|---|
|cosmosgen.py|Class containing main method as well as all command line interaction|[.py](../Autocoders/bin/cosmosgen.py)|