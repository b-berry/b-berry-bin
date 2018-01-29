#!/usr/bin/python
import csv
import czml
import geocoder
import os
import re
import simplekml
import sys
import time
from optparse import OptionParser
from shapely.geometry import Point

global ns 
ns = '{http://www.opengis.net/kml/2.2}'

def main():

    # Set default view => (range,heading,tilt)
    default_view = (1000.0,0.0,75.0) 

    parser = OptionParser()
    parser.add_option('-b', dest='bb',
            default=False, metavar='IMG', help='Create CZML:Billboard')
    parser.add_option('-c', '--czml', dest='czml',
        action='callback', callback=vararg_callback,
        default=False, help='Run geocode operation and output CZML')
    parser.add_option('-k', '--kml', dest='kml',
        action='callback', callback=vararg_callback,
        default=False, help='Run geocode operation and output KML')
    parser.add_option('-i', dest='infile',
            default=False, metavar='INFILE.csv', help='Create KML:Placemarks from file')
    #parser.add_option('-I', '--Inline', dest='inline',
    #    default=False, action='store_true', help='Write queries into single document')
    # This OPT behavior needs work:
    parser.add_option('-l', '--lookat', nargs=3, dest='lookAt',
        default=False, action='store', help=('Generate KML:LookAt   '
            'ex: -l <range> <heading> <tilt>'))
    parser.add_option('-q', '--quick', dest='quick',
        action='callback', callback=vararg_callback,
        default=False, help='Run quick geocode operation. ie \'seattle,wa\'')
    parser.add_option('-p', dest='place',
            default=False, metavar='PIN', help='Create KML:Placemark')
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
    #if options.inline:
    #    # Build single KML File
    #    print 'options.inline todo'
    #    exit(0)
    else:
        if options.czml:
            parse_czml(options)
        elif options.kml or options.infile:
            #import code; code.interact(local=dict(globals(), **locals()))
            if options.infile:
                parse_csv(options)
            else:
                parse_kml(options)
        else:
            print 'Options parse error.  Exiting'
            exit(1)


def init_czml():

    try:
        # Create root CZML && Document object
        c = czml.CZML()
        p = czml.CZMLPacket(id='document',version='1.0')
        c.packets.append(p)
        print 'OK'
        return c
    except:
        print 'FAIL'

def init_kml(name):

    # Create the root KML && Document object
    try:
        k = simplekml.Kml()
        k.document.name = name
        print 'OK'
        return k
    except:
        print 'FAIL'

def flyto_kml(gtx,point,view):

    #import code; code.interact(local=dict(globals(), **locals()))
    gxf = gtx.newgxflyto(gxduration=4)
    gxf.lookat.altitudemode = 'absolute'
    gxf.lookat.altitude = 0.0
    gxf.lookat.latitude = point['lat']
    gxf.lookat.longitude = point['lng']
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

def make_billboard(obj,point,img):

    try:
        # Define coord tuple
        coord = [ point['lng'], point['lat'], 150 ]

        # Create and append a billboard packet
        v = czml.Position(cartographicDegrees = coord)
        p = czml.CZMLPacket(id=point['address'], position=v)
        bb = czml.Billboard(scale=0.5, show=True)
        bb.image = img
        bb.color = {'rgba': [0, 255, 127, 55]}
        p.billboard = bb
        obj.packets.append(p)
        print 'OK'
    except:
        print 'FAIL'

def make_placemark(pnt,image):

    try:
        pnt.style.iconstyle.icon.href = image
        # For now, assume no label if placemark pin
        pnt.style.labelstyle.scale = 0
    except:
        print 'FAIL'

def make_point(obj,point):

    try:
        p = obj.newpoint(name=point['address'],coords=[(point['lng'],point['lat'],0.0)])
        return p
    except:
        print 'FAIL'

def parse_csv(options):

    try:
        base = os.path.basename(options.infile)
        name = re.sub('[^A-Za-z0-9]+','-',os.path.splitext(base)[0])
        print 'Parsing CSV: %s' %name
    except:
        print 'Error parsing filename'
        exit()

    # Initiate KML Document
    print 'Creating KML Document ',
    k = init_kml('Document')
    # Create Folder
    f = k.newfolder(name='Folder')

    # Read CSVFile from infile
    try:
        print 'Running opts for:'
        with open(options.infile) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                query = re.sub('[^A-Za-z0-9]+','-',
                    str(row['Location Name'] + ', ' + row ['Address'])
                )
                print '%s' %query,
                results = googleAPI(query)
                if not results:
                    continue
                else:
                    p = make_point(f,results)
                    if options.place:
                        make_placemark(p,options.place)
                # Sleep to meet API Restriction
                time.sleep(1.0)
            print 'Printing document: %s' %name,
            if options.write:
                write_kml(k,name)
            else:
                print_kml(k)
    except IOError:
        print 'FAIL'

def parse_czml(options):

    for query in options.czml:
        print 'Running opts for: %s' %query
        print '  Creating CZML Document: ',
        c = init_czml()
        if options.bb:
            name = re.sub('[^A-Za-z0-9]+', '-',
                query) + '-billboard'
            print '  Generating billboard: %s ' %name,
            results = googleAPI(query)
            make_billboard(c,results,options.bb)
        else: #Fix this
            name = re.sub('[^A-Za-z0-9]+', '-', query)
            results = googleAPI(query)

    print '  Printing document: %s' %name,
    write_czml(c,name + '.czml')

def parse_kml(options):

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
            w0 = gxt.newgxwait(gxduration=0.3)
            # Get user specified view
            if options.lookAt:
                view = options.lookAt
            else:
                view = default_view
            results = googleAPI(query)
            gxf = flyto_kml(gxt,results,view)
            # Add a gx:Wait for render
            w1 = gxt.newgxwait(gxduration=2.0)
        else:
            # Create Folder
            f = k.newfolder(name='Folder')
            results = googleAPI(query)
            p = make_point(f,results)
            if options.place:
                make_placemark(p,options.place)
            #name = re.sub('[^A-Za-z0-9]+', '-', address)
            place = p.__dict__['_placemark']
            name = re.sub('[^A-Za-z0-9]+', '-',
                place.__dict__['_kml']['name']) + '-lookat'
            if options.lookAt:
                lookat_kml(p,options.lookAt)
        if options.write:
            print '  Printing document: %s' %name,
            write_kml(k,name)
        else:
            # Print result KML
            print_kml(k)

def print_kml(doc):
   
    #import code; code.interact(local=dict(globals(), **locals()))
    print doc.kml() 

def write_czml(doc,filename):

    try:
        if filename.lower().endswith('.czml'):
            doc.write(filename)
        else:
            doc.write(filename + '.czml')
        print 'OK'
    except:
        print 'FAIL'

def write_kml(doc,filename):

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
        results = {}
        g = geocoder.google(query).geojson
        results = g['features'][0]['properties']
        print 'OK'
        return results
    except:
        print 'FAIL'
        return False
        #exit(2)

def quick(args):

    try:
        for query in args:
            if query == args[0] or query.startswith('-'):
                next
            else:
                results = googleAPI(query)
                # Print Results
                print ('Query: %s'
                       '\n\tAddress: %s'
                       '\n\tLongitude: %s'
                       '\n\tLatitude: %s' %(query,results['address'],results['lng'],results['lat'])
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
