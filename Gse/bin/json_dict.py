# Sanchit Sinha
# Create OpenMCT formatted dictionary of channels

import os
import sys
import json

from optparse import OptionParser

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/../src')

from controllers import channel_loader, event_loader, command_loader
__updated__ = '2017-08-25'
def main(argv=None):


    program_license = "Copyright 2015 user_name (California Institute of Technology)                                            \
            ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged."
    program_version = "v0.1"
    program_build_date = "%s" % __updated__
    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''''' # optional - give further explanation about what the program does

    if argv is None:
        argv = sys.argv[1:]

    parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
    parser.add_option("-s", "--source", dest="source", action="store", type="string", help="Set source of generated dictionaries [default: %default]", \
                     default=os.path.dirname(os.path.realpath(__file__)) + '/../generated/Ref')
    parser.add_option("-d", "--destination", dest="destination", action="store", type="string", help="Set directory of JSON library [default: %default]", \
                     default=os.path.dirname(os.path.realpath(__file__)) + '/../client-openmct/server/res/')
    parser.add_option("-n", "--name", dest="name", action="store", type="string", help="Set name of target [default: %default]", \
                     default='ref')

    # process options
    (opts, args) = parser.parse_args(argv)

    # Set path
    dir_path = opts.source
    sys.path.append(dir_path)

    # Set save path
    save = opts.destination + 'dictionary.json'

    # Set name
    target_name = opts.name

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
        if ch_cd[id]["type"] == "Enum":
            enum_dict = {v:k for k,v in cl.getTypesDict()[id].enum_dict().iteritems()}
            ch_cd[id]["enum_dict"] = enum_dict

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
            toAppend = {
                "name": arg[0],
                "description": arg[1],
                "type": arg[2].__repr__(),
            }
            if toAppend["type"] == "Enum":
                toAppend["enum_dict"] = arg[2].enum_dict()
            co_cd[co.getOpCodeDict()[name]]["arguments"].append(toAppend)

    final_dict = {
        target_name: {
            "channels": ch_cd,
            "events": ev_cd,
            "commands": co_cd
        }
    }
    
    with open(save, 'w') as fp:
        json.dump(final_dict, fp, sort_keys=True, indent=4)

    return (save, target_name)

if __name__ == "__main__":
    save_name, target_name = main()
    print "Saved: " + save_name
    print "Target: " + target_name
