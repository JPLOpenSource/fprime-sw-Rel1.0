#!/bin/env python

import os
import sys
from cosmos.gse_api import GseApi
from optparse import OptionParser

__version__ = 0.1
__date__ = '2018-08-20'
__updated__ = '2018-08-20'

def main(argv=None):

    if argv is None:
        argv =sys.argv[1:]
    try:
        program_name = os.path.basename(sys.argv[0])
        program_version = "v0.1"
        program_build_date = "%s" % __updated__
        program_longdesc = '''''' # optional - give further explanation about what the program does
        program_license = "Copyright 2018 aarondou (California Institute of Technology)                                            \
                ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged."

        program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
        if argv is None:
            argv = sys.argv[1:]

        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-d", "--dictionary", dest="generated_path", action="store", type="string", \
                help="Set base path to generated command/telemetry definition files")
        parser.add_option("-a", "--addr", dest="addr", action="store", type="string", help="set threaded tcp socket server address [default: %default]", \
                default="127.0.0.1")
        parser.add_option("-p", "--port", dest="port", action="store", type="int", help="Set threaded tcp socket server port [default: %default]", \
                default=7777)
        parser.add_option("-m", "--monitor", dest="monitor", action="store", type="string", help="Set type of telemetry to monitior [default: %default]", \
                default='ch')
        (opts, args) = parser.parse_args(argv)

        api = GseApi(generated_path=opts.generated_path, server_addr=opts.addr, port=opts.port, verbose=True)
        if opts.monitor == 'evr':
            print 'Listening for event telemetry'
            api.monitor_evr()
        else:
            print 'Listening for channelized telemetry'
            api.monitor_tlm()

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2

if __name__ == "__main__":
    main()
