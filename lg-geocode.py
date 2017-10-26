#!/usr/bin/python

import geocoder
import simplekml
import sys
from optparse import OptionParser

global ns 
ns = '{http://www.opengis.net/kml/2.2}'

def main():

    # Set default view => (range,heading,tilt)
    default_view = (1000.0,0.0,75.0) 

    parser = OptionParser()
    parser.add_option('-k', '--kml', dest='kml',
        action='callback', callback=vararg_callback,
        default=False, help='Run geocode operation and output KML')
    # This OPT behavior needs work:
    parser.add_option('-l', '--lookat', nargs=3, dest='lookAt',
        default=default_view, action='store', help=('Generate KML:LookAt   '
            'ex: -l <range> <heading> <tilt>'))
    parser.add_option('-q', '--quick', dest='quick',
        action='callback', callback=vararg_callback,
        default=False, help='Run quick geocode operation. ie Provide string queries as args')
    parser.add_option('-w', '--write', dest='write',
        default=False, metavar='FILE', help='Write results to FILE')
    (options, args) = parser.parse_args()

    print options
    #import code; code.interact(local=dict(globals(), **locals()))

    if options.quick:
        quick(sys.argv)
    if options.kml:
        # Initiate KML Document
        k = init_kml('Document')
        # Create Folder
        f = k.newfolder(name='Folder')
        # Parse arg queries
        for query in options.kml:
            g = googleAPI(query)
            address = g['features'][0]['properties']['address']
            coord = g['features'][0]['geometry']['coordinates']
            p = f.newpoint(name=query,coords=[(coord[0],coord[1],0.0)])
            lookat_kml(p,options.lookAt)
        # Print result KML
        print_kml(k)

def init_kml(name):

    # Create the root KML && Document object
    k = simplekml.Kml()
    k.document.name = name
    return k

def lookat_kml(point,view):

    point.lookat.altitudemode = 'absolute'
    point.lookat.altitude = 0.0
    point.lookat.latitude = point.coords.__dict__['_coords'][0][1] 
    point.lookat.longitude = point.coords.__dict__['_coords'][0][0]
    point.lookat.range = view[0]
    point.lookat.heading = view[1]
    point.lookat.tilt = view[2]
    #import code; code.interact(local=dict(globals(), **locals()))

    return point

def print_kml(doc):
    
    print doc.kml() 

def googleAPI(query):

    try:
        g = geocoder.google(query)
        return g.geojson
    except:
        print 'Geocode lookup on query: %s FAIL' %query
        exit(2)

def quick(args):

    try:
        for query in args:
            if query == args[0] or query.startswith('-'):
                next
            else:
                g = googleAPI(query)
                # Print Results
                address = g['features'][0]['properties']['address']
                coord = g['features'][0]['geometry']['coordinates']
                print ('Query: %s'
                       '\n\tAddress: %s'
                       '\n\tLongitude: %s'
                       '\n\tLatitude: %s' %(query,address,coord[0],coord[1])
                      )
    except ValueError:
        print 'Error: queries not iterable as given'
        exit(1)

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
