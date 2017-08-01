# Sanchit Sinha
# Create OpenMCT formatted dictionary of channels

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/../src')

from controllers import channel_loader, event_loader, command_loader

# Set path
dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../generated/Ref'
sys.path.append(dir_path)

# Create channel loader object
cl = channel_loader.ChannelLoader.getInstance()
cl.create(dir_path + '/channels')

# Create event loader object
el = event_loader.EventLoader.getInstance()
el.create(dir_path + '/events')

# Create command loader object
co = command_loader.CommandLoader.getInstance()
co.create(dir_path + '/commands')

# Create channel combined dictionary
ch_cd = {}
for id in cl.getNameDict():
    ch_cd[id] = {}

for id in ch_cd:
    ch_cd[id]["id"]            = id
    ch_cd[id]["name"]          = cl.getNameDict()[id]
    ch_cd[id]["telem_type"]    = "channel"
    ch_cd[id]["component"]     = cl.getCompDict()[id]
    ch_cd[id]["description"]   = cl.getChDescDict()[id]
    ch_cd[id]["units"]         = cl.getUnitsDict()[id]
    ch_cd[id]["type"]          = cl.getTypesDict()[id].__repr__()
    ch_cd[id]["format_string"] = cl.getFormatStringDict()[id]
    ch_cd[id]["limits"]        = {
                                    "low_red": cl.getLowRedDict()[id],
                                    "low_orange": cl.getLowOrangeDict()[id],
                                    "low_yellow": cl.getLowYellowDict()[id],
                                    "high_yellow": cl.getHighYellowDict()[id],
                                    "high_orange": cl.getHighOrangeDict()[id],
                                    "high_red": cl.getHighRedDict()[id]
                                 }

# Add events channel
ch_cd[-1] = {
    "id": -1,          
    "name": "Events", 
    "telem_type": "channel",
    "component": None,
    "description": "Events are shown here",
    "type": "string",
    "format_string": None
}

# Create event combined dictionary
ev_cd = {}
for id in el.getNameDict():
    ev_cd[id] = {}

for id in ev_cd:
    ev_cd[id]["id"]            = id
    ev_cd[id]["name"]          = el.getNameDict()[id]
    ev_cd[id]["telem_type"]    = "event"
    ev_cd[id]["severity"]      = str(el.getSeverity()[id])[len('Severity.'):]
    ev_cd[id]["format_string"] = el.getFormatString()[id]
    arguments = [];
    for argument in el.getEventDesc()[id]:
        arg = argument[2].__repr__()
        if arg == 'Enum':
            enum_dict = {v:k for k,v in argument[2].enum_dict().iteritems()}    # switch key,value pair
            arguments.append(enum_dict)
        else:
            arguments.append(arg)
    ev_cd[id]["arguments"] = arguments

co_cd = {}
for name in co.getOpCodeDict():
    co_cd[co.getOpCodeDict()[name]]                = {}
    co_cd[co.getOpCodeDict()[name]]["id"]          = co.getOpCodeDict()[name]
    co_cd[co.getOpCodeDict()[name]]["component"]   = co.getComponentsDict()[name]
    co_cd[co.getOpCodeDict()[name]]["description"] = co.getDescDict()[name]
    co_cd[co.getOpCodeDict()[name]]["name"]        = name
    co_cd[co.getOpCodeDict()[name]]["arguments"]   = []
    for arg in co.getArgsDict()[name]:
        co_cd[co.getOpCodeDict()[name]]["arguments"].append({
            "name": arg[0],
            "description": arg[1],
            "type": arg[2].__repr__()
        })

final_dict = {
    "isf": {
        "channels": ch_cd,
        "events": ev_cd,
        "commands": co_cd
    }
}

save = os.path.dirname(os.path.realpath(__file__)) + '/../../Client-OMCT/server/res/dictionary.json'
with open(save, 'w') as fp:
    json.dump(final_dict, fp, sort_keys=True, indent=4)
 
if __name__ == "__main__":
    print "Saved: " + save