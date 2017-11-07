#!/usr/bin/python

import geocoder
import re
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
    parser.add_option('-i', '--inline', dest='inline',
        default=False, action='store_true', help=('Combine queries as single ' 
            'KML document'))
    # This OPT behavior needs work:
    parser.add_option('-l', '--lookat', nargs=3, dest='lookAt',
        default=default_view, action='store', help=('Generate KML:LookAt   '
            'ex: -l <range> <heading> <tilt>'))
    parser.add_option('-q', '--quick', dest='quick',
        action='callback', callback=vararg_callback,
        default=False, help='Run quick geocode operation. ie Provide string queries as args')
    parser.add_option('-t', '--tour', dest='tour',
        default=False, action='store_true', help='Generate KML:gx:Tour')
    parser.add_option('-w', '--write', dest='write',
        default=False, action='store_true', help='Write results to FILE')
    (options, args) = parser.parse_args()

    print options
    #import code; code.interact(local=dict(globals(), **locals()))

    if options.quick:
        quick(sys.argv)
        exit(0)
    if options.kml:
        if options.inline:
            # Build single KML File
            print 'options.inline todo'
            exit(0)
        else:
            # Parse arg queries
            for query in options.kml:
                print 'Running opts for: %s' %query
                # Initiate KML Document
                print '  Creating KML Document ',
                k = init_kml('Document')
                # Create Network Link for gx:Tours
                if options.tour:
                    print '  Creating NetworkLink:Autoplay ',
                    make_autoplay(k)
                    name = re.sub('[^A-Za-z0-9]+', '-',
                        query) + '-tour'
                    print '  Generating gx:Tour ',
                    gxt = init_kml_tour(k)
                    # Add a gx:Wait init to reduce problems
                    gxt.newgxwait(gxduration=0.3)
                    # Get user specified view
                    if options.lookAt:
                        view = options.lookAt
                    else:
                        view = default_view
                    gxf = flyto_kml(gxt,query,view)
                    # Add a gx:Wait for render
                    gxt.newgxwait(gxduration=2.0)
                else:
                    # Create Folder
                    f = k.newfolder(name='Folder')
                    p = make_point(f,query)
                    #name = re.sub('[^A-Za-z0-9]+', '-', address)
                    place = p.__dict__['_placemark']
                    name = re.sub('[^A-Za-z0-9]+', '-',
                        place.__dict__['_kml']['name']) + '-lookat'
                    lookat_kml(p,options.lookAt)
                if options.write:
                    print '  Printing document: %s' %name,
                    write_kml(k,name)
                else:
                    # Print result KML
                    print_kml(k)


def init_kml(name):

    # Create the root KML && Document object
    try:
        k = simplekml.Kml()
        k.document.name = name
        print 'OK'
        return k
    except:
        print 'FAIL'

def flyto_kml(gtx,query,view):

    g = googleAPI(query)
    address = g['features'][0]['properties']['address']
    coord = g['features'][0]['geometry']['coordinates']

    #import code; code.interact(local=dict(globals(), **locals()))
    gxf = gtx.newgxflyto(gxduration=4)
    gxf.lookat.altitudemode = 'absolute'
    gxf.lookat.altitude = 0.0
    gxf.lookat.latitude = coord[1]
    gxf.lookat.longitude = coord[0]
    gxf.lookat.range = view[0]
    gxf.lookat.heading = view[1]
    gxf.lookat.tilt = view[2]
    return gxf

def init_kml_tour(f):

    try:
        t = f.newgxtour(name='Play-Tour')
        print 'OK'
        return t.newgxplaylist()
    except:
        print 'FAIL'

def lookat_kml(p,view):

    p.lookat.altitudemode = 'absolute'
    p.lookat.altitude = 0.0
    p.lookat.latitude = p.coords.__dict__['_coords'][0][1] 
    p.lookat.longitude = p.coords.__dict__['_coords'][0][0]
    p.lookat.range = view[0]
    p.lookat.heading = view[1]
    p.lookat.tilt = view[2]
    return p

def make_autoplay(k):

    try:
        nl = k.newnetworklink(name='Autoplay')
        nl.link.href = 'http://localhost:8765/query.html?query=playtour=Play-Tour'
        nl.link.viewrefreshmod = simplekml.ViewRefreshMode.onrequest
        print 'OK'
    except:
        print 'FAIL'

def make_point(obj,query):

    g = googleAPI(query)
    address = g['features'][0]['properties']['address']
    coord = g['features'][0]['geometry']['coordinates']

    p = obj.newpoint(name=query,coords=[(coord[0],coord[1],0.0)])
    return p

def print_kml(doc):
   
    print doc.kml() 

def write_kml(doc,filename):

    #import code; code.interact(local=dict(globals(), **locals()))
    # Detect KMZ 
    try:
        if filename.lower().endswith('.kmz'):
            doc.savekmz(filename)
        # Write KML
        elif filename.lower().endswith('.kml'):
            doc.save(filename)
        else:
            # Add extension to filename
            doc.save(filename.lower() + '.kml')
        print 'OK'
    except IOError:
        print 'FAIL'


def tour_kml(view):

    print 'Generate Tour here'

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
