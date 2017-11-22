#!/bin/bash
# vim: set tabstop=2:
# vim: set shiftwidth=2:

# A POSIX variable
OPTIND=1 

function show_help() {

  echo "Usage: $(basename $0):"
  echo " -h     Show this help message"
  echo " -c     Clone from gitlabs:lg-content-dev"
  echo " -g     Clond from github:EndPointCorp"
  echo " -l     Clone from gitlabs:default"

}

USER='git'
while getopts "h?c:g:l:" opt; do
  case $opt in
    h|\?)
      show_help
      exit 0
      ;;
    c)
      ORIGIN="bits.endpoint.com"
      REPO="lg-content-dev/$OPTARG"
      ;;
    g)
      ORIGIN="github.com:EndPointCorp"
      REPO=$OPTARG
      ;;
    l)
      ORIGIN="bits.endpoint.com"
      REPO=$OPTARG
      ;;
    *)
      show_help
      exit 1
  esac
done

shift $((OPTIND-1))

if [ $OPTIND -lt 2 ]; then
  show_help
  exit 1
else
  CMD="git clone $USER@${ORIGIN}/${REPO}.git"
  printf "Attempting: $CMD "
  $($CMD)
  C_STATUS=$?
  if [ $C_STATUS -gt 0 ]; then
    echo "FAIL"
  else 
    echo "OK"
  fi
fi
