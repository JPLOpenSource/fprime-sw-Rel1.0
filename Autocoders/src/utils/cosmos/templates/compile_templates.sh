# Script to compile every cheetah template for cosmosgen.py

echo "Compiling Cheetah Templates"

cheetah compile Channel.tmpl
cheetah compile Channel_Screen.tmpl
cheetah compile Event.tmpl
cheetah compile Command.tmpl
cheetah compile Data_Viewer_Config.tmpl
cheetah compile Tlm_Viewer_Config.tmpl
cheetah compile System.tmpl
cheetah compile Cosmos_Server.tmpl
cheetah compile Data_Viewer.tmpl
cheetah compile Server_Config.tmpl
cheetah compile Target.tmpl
cheetah compile Channel_Partial.tmpl
cheetah compile Command_Partial.tmpl
cheetah compile Event_Partial.tmpl
cheetah compile Data_Viewer_Partial.tmpl
