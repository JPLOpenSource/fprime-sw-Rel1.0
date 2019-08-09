# fprime

This is an old unofficial fprime repo that contains some ground support equipment software work using the ZeroMq middleware libraries.  It contains a prototype Python ZeroMQ pub/sub server that can be used with the Zmq-Radio component that is found in the fprime-zmq/zmq-radio Fprime component.  All of this is here as is and has not been recently tested.

The Python ZeroMq Pub/Sub Server is located in

   Gse/bin/run_zmq_server.py
   Gse/src/server

Some start up information for executing it is in the fprime-zme/README.md file.

NOTE if you have stubled on to this repo the official fprime release can be found at https://github.com/nasa/fprime.  This release has the Gse removed and refactored into a new Gds area.  It also using a newer cmake based make system.

Branchs:

Rel1.0 - This branch with the experimental ZeroMQ stuff.

cosmos - In Autocoders/bin a cosmos configuration generator.  This produces configuration for the COSMOS GSE tool located at https://cosmosrb.com.  It configures the cosmos server to connect up to the Ref app which uses TCP socket connection.  The Ref app is the client.

openmct - This branch has an experimental OpenMCT configuration and Node.js server for it.  The Node.js app connects to the old Gse TCP socket server and provies a web socket interface to OpenMCT.  There is a ReadMe.md file in the openmct directory. Information on OpenMCT is located at https://nasa.github.io/openmct/.

Questions about this repo can be sent to reder@jpl.nasa.gov 



F' Release Notes

Release 1.0: 

This is the initial release of the software to open source. See the license file for terms of use.

An architectural overview of the software can be found [here.](docs/Architecture/FPrimeArchitectureShort.pdf)

A user's guide can be found [here.](docs/UsersGuide/FprimeUserGuide.pdf)
   
Documentation for the Reference example can be found [here.](Ref/docs/sdd.md)

Release 1.01

Updated contributor list. No code changes. 
