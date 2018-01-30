#!/bin/bash

# Clean asset files not in ros_cms dtabase

MEDIA_DIR='/media/lgmedia/ros_cms_default_assets'
ROS_CMS_DIR='/srv/ros_cms'
ROS_CMS_ENV="$ROS_CMS_DIR/shared/env/bin"
LGISCMS_DIR="$ROS_CMS_DIR/current/lgiscms"

function usage {

     echo "Usage: $1 OPT"
     echo "  OPT: --ros_cms|-r Run Check from ros_cms database"
     echo "       --lgmedia|-m Run Check from lgmedia filesystem"
     exit 1

}

function activate_env {

  if [ ! -f "$LGISCMS_DIR/manage.py" ]; then
    printf "$LGISCMS_DIR/manage.py Not Found! "
    echo 'FAIL' && exit 1
  fi
  eval source $ROS_CMS_ENV/activate

}

function check_cms_files {

  while read ASSET; do
    printf "$ASSET: "
    if [ -f "$MEDIA_DIR/$ASSET" ]; then
      echo 'OK'
    else
      echo 'FAIL'
    fi
  done< <(eval ./manage.py listfiles | sed -e '/^$/d')

}

function check_files_in_cms {

  # Not very efficient here fix it
  DATE=$(date +%Y%m%d-%HM%S)
  TMP_DIR="clean-tmp-$DATE"
  MANIFEST="$TMP_DIR/ros_cms.files"
  mkdir -p ".$TMP_DIR" &&\
  eval ./manage.py listfiles | sed -e '/^$/d' > $MANIFEST
  if [ ! -f $MANIFEST ]; then
    echo "ERROR: Encountered file write error: Exiting!"
    exit 2
  fi
  while read FILE; do
    printf "$FILE: "
    # if file in database
    ASSET=$(basename $FILE)
    eval grep $ASSET $MANIFEST
    status=$?
    if [ $status -gt 0 ]; then
      echo 'OK'
    else
      if [ "$ACT" == "True" ]; 
        # Run action
        echo 'FAIL'
      else
        echo 'FAIL'
      fi
    fi
  done< <(find "$MEDIA_DIR/" -max-depth 1 -type f)

}

# Run Opts
while [ $# -gt 0 ]; do
  case $1 in
    --help|-h)
    usage $0
    ;;
    --ros_cms|-r)
      shift
      OPT="CMS"
    ;;
    --lgmedia|-m)
      OPT="MEDIA"
    ;;
    --force|-f)
      ACT="True"
    ;;
    *)
      usage $0
    ;;
  esac
  shift
done
if [ -z $OPT ]; then
  usage $0
fi

# Check Python Env state
PYTHON=$(which python)
if [ "$PYTHON" != "$ROS_CMS_ENV/python" ]; then
  echo "ENV: No ros_cms virtual env detected, attempting activation"
  activate_env
else
  echo "ENV: ros_cms virtual env detected, running actions:"
fi

pushd $LGISCMS_DIR &&\
case $OPT in
  CMS)
    check_cms_files
  ;;
  MEDIA)
    check_files_in_cms
  ;;
esac
echo 'Done.' && popd
