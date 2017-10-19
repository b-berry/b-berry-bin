#!/bin/bash

URL='https://montage.galaxy.endpoint.com/montage/images/lg-montage'

if [[ -z $1 ]]; then
    echo "You must supply a hostname!"
    exit 1
else
    display -geometry "50%"< <(curl --anyauth -u 'bryan' --digest "${URL}_${1}.png")
    echo "Done."
fi
