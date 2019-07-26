#!/bin/bash

LAUNCH_DHS_URI='https://quickconnect.dhs.gov'

function usage() {
  echo "$0 [-b|--browser] [-u|--url] [-h|--help]"
  exit 0
}

OPTIONS=()
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -b|--browser)
      USER_BROWSER="$2"
      shift
      shift
      ;;
    -u|--url)
      USER_URI="$2"
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
set -- "${OPTIONS[@]}"

BROWSER="${USER_BROWSER:-Safari}"
URI="${USER_URI:-$LAUNCH_DHS_URI}"

if [ ! -x $(command -v $BROWSER) ]; then
  echo "Error: Browser not found $BROWSER"
  exit 1
fi

cmd="open -a $BROWSER $URI"
echo"Initiating Command: $cmd"
eval $cmd
