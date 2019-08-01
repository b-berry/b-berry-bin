#!/bin/bash
# Dependencies:
# - Requires PIV Card to be inserted for Cert/Pin Verification

#set -x

DOWNLOAD_DIR="$HOME/Downloads"
DOWNLOAD_TYPE='ica'
LAUNCH_DHS_URI='https://quickconnect.dhs.gov'
SQLITE_DIR="$HOME/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2"

function usage() {
  echo "$0 [-b|--browser] [-d|--download-dir] [-t|--download-type] [-u|--url] [-x|--express] [-h|--help]"
  exit 0
}

function find_latest() {
  find_file="$(find $1 -name \"*.${2}\" -print0 | xargs -0 ls -t | head -1)"
  echo $find_file
}

function open_browser() {
  if [ ! -x $(command -v $1) ]; then
    echo "Error: Browser not found $1"
    exit 1
  else
    cmd="open -a $1 $2"
    echo "Initiating Command: $cmd"
    eval $cmd
  fi
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
    -e|--express)
      user_launch_web=false
      shift
      shift
      ;;
    -t|--download-type)
      user_download_type="$2"
      shift
      shift
      ;;
    -u|--url)
      user_download_uri="$2"
      shift
      shift
      ;;
    -x|--exit)
      user_exit_after_download=true
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
download_type="${user_download_type:-$DOWNLOAD_TYPE}"
launch_web="${user_launch_web:-true}"
exit_after_download="${user_exit_after_download:-false}"
download_uri="${user_download_uri:-$LAUNCH_DHS_URI}"

if $launch_web; then
  echo "Launching: $browser"
  open_browser $browser $download_uri
else
  echo "Skipping: User specified -e|--express to skip browser launch"
fi

if $exit_after_download; then
  echo "Exiting: User specified -x|--exit"
  exit 0
fi

echo "Waiting for user to proceed.  Ready (press any key)"
read user_input

#dataurlstring=read_data $SQLITE_DIR $browser
#echo $dataurlstring
citrix_file="$(find_latest $download_dir $download_type)"
#echo $citrix_file
open -a Citrix\ Workspace "$citrix_file"
