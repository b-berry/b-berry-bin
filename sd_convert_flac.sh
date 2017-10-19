#!/bin/bash

FILETYPES="*.{FLAC,JPG,JPEG,MP3,PNG,WAV}"

# If no cli opt try to find mount point
if [[ -z $1 ]]; then
  DIRNAME="SPORT PLUS"
  MOUNTPOINT=$(find /media/ -name $DIRNAME -type d  -print -quit 2>/dev/null)
  # Report error
  if [[ -z $MOUNTPOINT ]]; then
    echo "Mount point not found!"
    echo "Please provide a mount point dir for SanDisk device"
    exit 1
  fi
fi

# Find files
while read FILE; do
  OUTFILE="${FIL%.*}.flac"
  ffmpeg -i $FILE -f flac $OUTFILE
done< <(find "$MOUNTPOINT/Music/" -type f -not -iname "$FILETYPES")
