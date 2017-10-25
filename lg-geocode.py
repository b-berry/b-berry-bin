#!/usr/bin/python

import geocoder
import sys

if len(sys.argv) < 1:
    print 'Please specify a lookup query'
    print '  ex: \'Seattle, WA'
    exit(1)
else:
    for query in sys.argv:
        if query == sys.argv[0]:
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
            print 'Query: %s\n\tAddress: %s\n\tLongitude: %s\n\tLatitude: %s' %(query,address,coord[0],coord[1])
