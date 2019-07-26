#!/bin/bash
# Dependencies:
# - Requires PIV Card to be inserted for Cert/Pin Verification

set -x

DOWNLOAD_DIR='/Users/bryan.berry/Downloads'
LAUNCH_DHS_URI='https://quickconnect.dhs.gov'
SQLITE_DIR="~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2"

function usage() {
  echo "$0 [-b|--browser] [-u|--url] [-h|--help]"
  exit 0
}

function open_browser() {
  if [ ! -x $(command -v $1) ]; then
    echo "Error: Browser not found $1"
    exit 1
  else
    cmd="open -a $1 $2"
    echo"Initiating Command: $cmd"
    eval $cmd
  fi
  echo "Waiting for user to proceed.  Ready (press any key)"
  read user_input
}

function read_data() {
  echo "Attempting to extract downloaded file from: $SQLITE_DIR"
  #dataurlstring=$(sqlite3 $1 "select LSQuarantineDataURLString from LSQuarantineEvent where LSQuarantineAgentName = \"${2}\" order by LSQuarantineTimeStamp desc limit 1")
  return sqlite3 $1 "select LSQuarantineDataURLString from LSQuarantineEvent order by LSQuarantineTimeStamp desc limit 1"
}

options=()
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -b|--browser)
      user_browser="$2"
      shift
      shift
      ;;
    -d|--download-dir)
      user_download_dir="$2"
      shift
      shift
      ;;
    -u|--url)
      user_uri="$2"
      shift
      shift
      ;;
    -x|--express)
      user_express=true
      shift
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done
set -- "${options[@]}"

browser="${user_browser:-Safari}"
download_dir="${user_download_dir:-$DOWNLOAD_DIR}"
uri="${user_uri:-$LAUNCH_DHS_URI}"
user_express="${user_express:-false}
"
if [ ! $user_express ]; then
  open_browser $browser $uri
fi

dataurlstring=read_data $SQLITE_DIR $browser
echo $dataurlstring
