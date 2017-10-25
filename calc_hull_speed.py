#!/usr/bin/python

import argparse
import math

parser = argparse.ArgumentParser()
parser.add_argument('-f','--feet', help='Consider input value in units of feet')
parser.add_argument('-m','--meters', help='Consider input value in units of meters')
args = parser.parse_args()

def calcHullSpeed(length):
    return 1.34 * math.sqrt(length)

def convertMeters(meters):
    return 3.28084 * meters

def get_units(args):
    # Handle meters
    if args.meters:
        length = convertMeters(float(args.meters))
        units = 'm'
    else:
        length = args.feet
        units = 'ft'
    return length,units

# Handle arguments
length,units = get_units(args)

# Call calc()
h_speed = calcHullSpeed(float(length))
print 'LWL: %s%s  Hull Speed: %s%s' %(length,units,h_speed,'kts')
