#!/bin/bash

LAUNCH_CONFIG_SOURCE="$HOME/Downloads/sys/launch.ica"
LAUNCH_CONFIG_TARGET="${LAUNCH_CONFIG_SOURCE%*.ica}-petco-vdi-restore.ica"

if [ -f $LAUNCH_CONFIG_SOURCE ]; then
  echo "Found source config: $LAUNCH_CONFIG_SOURCE"
  echo "Creating launch config: $LAUNCH_CONFIG_TARGET"
  cp -vf $LAUNCH_CONFIG_SOURCE $LAUNCH_CONFIG_TARGET
  cmd="open $LAUNCH_CONFIG_SOURCE -a Citrix\ Receiver"
  eval $cmd
else
  echo "Source config not found: $LAUNCH_CONFIG_SOURCE"
  exit 1
fi
