#!/usr/bin/python

import geocoder
import sys
from optparse import OptionParser

def main():

    parser = OptionParser()
    parser.add_option("-q", "--quick", dest="quick",
        action="callback", callback=vararg_callback,
        default=False, help="Run quick geocode operation. ie Provide string queries as args")

    (options, args) = parser.parse_args()

    #print options
    #import code; code.interact(local=dict(globals(), **locals()))

    if options.quick:
        quick(sys.argv)

def quick(args):

        if len(args) < 1:
            print 'Please specify a lookup query'
            print '  ex: \'Seattle, WA'
            exit(1)
        else:
            for query in args:
                if query == args[0] or query == '-q':
                    next
                else:
                    try:
                        # Try LookUp
                        g = geocoder.google(query).geojson
                    except:
                        print 'Geocode lookup on query: %s FAIL' %query
                        exit(2)

                    # Print Results
                    address = g['features'][0]['properties']['address']
                    coord = g['features'][0]['geometry']['coordinates']
                    print ('Query: %s'
                           '\n\tAddress: %s'
                           '\n\tLongitude: %s'
                           '\n\tLatitude: %s' %(query,address,coord[0],coord[1])
                          )

def vararg_callback(option, opt_str, value, parser):
    assert value is None
    value = []

    def floatable(str):
        try:
            float(str)
            return True
        except ValueError:
            return False

    for arg in parser.rargs:
        # stop on --foo like options
        if arg[:2] == "--" and len(arg) > 2:
            break
        # stop on -a, but not on -3 or -3.0
        if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
            break
        value.append(arg)

    del parser.rargs[:len(value)]
    setattr(parser.values, option.dest, value)

# Execute Script
if __name__ == '__main__':
    main()
