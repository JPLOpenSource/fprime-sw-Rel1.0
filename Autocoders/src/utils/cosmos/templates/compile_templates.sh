#!/bin/csh

echo "Compiling Cheetah Templates"

cheetah compile Channel.tmpl
cheetah compile Channel_Screen.tmpl
cheetah compile Event.tmpl
# cheetah compile Command.tmpl
# cheetah compile Target.tmpl
# cheetah compile System.tmpl
# cheetah compile Cosmos_Server.tmpl
# cheetah compile Data_Viewer.tmpl
