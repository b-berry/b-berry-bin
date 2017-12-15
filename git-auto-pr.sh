#!/bin/bash

function run_cmd() {

  echo "Command: $1"
  echo "Run this command? [Yes/No]"
  # Ask User confirmation
  read RUN

  case $RUN in
    [yY]|[yY]es)
      echo "Running: $CMD"
      $CMD
      ;;
    [nN]|[nN]o)
      echo "User rejected run: Exiting!"
      exit 0
      ;;
  esac

}

function test_str() {

  # Test Results 
  printf "Testing string: $1 "
  if [[ -z "$1" ]]; then
    # REMOTE empty, exit
    echo "FAIL"
    exit 1
  fi
  echo "OK"

}

# Get current branch
BRANCH=$(git branch | grep \* | awk -F ' ' '{print $2}')
test_str "$BRANCH"
# Map current branch to remote track
REMOTE=$(git branch -r | grep $BRANCH | sed -e 's/\ //g' | sed -e 's:/:\ :g')
test_str "$REMOTE"
# Define CMD
CMD="git pull --rebase ${REMOTE}"
run_cmd "$CMD"
# Ask to push if pr successful
if [ $? -lt 1 ]; then
  CMD="git push ${REMOTE}"
  run_cmd "$CMD"
fi
