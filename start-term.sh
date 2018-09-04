#!/bin/bash

GEOMETRY_G='155x45+38+48'
GEOMETRY_X='155x45+35+50'
PROFILE='default'
SESS='desktop'

function construct_proj {

  # This will be were project stuff happens
  return

}


function build_tmux {

  STATUS=0
  T_SESS=$1
  PROJ=$2

  if [ -z $PROJ ]; then
    PROJ="src"
  fi

  # Set up window names : => dir
  declare -a conf_tmux=('me' 'far' 'near' ":$PROJ" 'ops' '5')

  first=true
  for n in $(seq 0 $(echo "${#conf_tmux[@]}-1" | bc)); do
    INSTANCE="${conf_tmux[$n]}"
    # Sort item type
      if [[ $INSTANCE == *":"* ]]; then
          NAME="${INSTANCE#:*}"
          if [ -d $NAME ]; then
            DIR=$NAME
          else
            echo "Debug 2b"
            DIR=$(find $HOME/* -maxdepth 1 -type d -name $(basename $NAME))
            # Correct dir if not found
            if [ ! -d $DIR ]; then
              echo "Debug 3"
              DIR=$HOME
            fi
          fi
      else
          NAME=${conf_tmux[$n]}
          DIR=$HOME
      fi
      # If first create session
      if $first; then
          echo "Initiating tmux session: $T_SESS:$NAME"
          tmux new-sess -d -s $T_SESS -n $(basename $NAME)
          T_STATUS=$?
          if [ $T_STATUS -lt 1 ]; then
              first=false
              continue
          fi
      fi
      # Build item in tmux
      printf "Building tmux new-window $NAME:$DIR "
      tmux new-window -d -c $DIR -n $(basename $NAME) -t $T_SESS
      N_STATUS=$?
      if [ $N_STATUS -ne 0 ]; then
          (( STATUS + 1 ))
          printf "FAIL\n"
      else
          printf "OK\n"
      fi
  done

  report_error $STATUS
}

function get_env {

  printf 'Detecting WM Env: '
  if [[ ( ! -z $XDG_CURRENT_DESKTOP ) || ( ! -z $GDMSESSION ) ]]; then
    printf 'OK\n  Desktop: %s\n  Session: %s\n' "$XDG_CURRENT_DESKTOP" "$GDMSESSION"
    SET_ENV=$GDMSESSION
    return
  elif [ $TERM_PROGRAM == "Apple_Terminal" ]; then
    printf 'OK\n  Desktop: %s\n  Session: %s\n' "$TERM_PROGRAM" "$LOGNAME"
    SET_ENV="apple"
  else
    printf 'ERROR\n'
  fi

}

function get_tmux {

    # Set up or join exiting tmux env
    tmux has-sess -t $1
    T_STATUS=$?
    if [ $T_STATUS -gt 0 ]; then
       # Create session
       echo "No tmux:$1 found... initiating"
       build_tmux $1 $2
    else
       echo "Found existing tmux: $1"
       return
    fi

}

function report_error {

    ERRORS=$1
    echo "Encountered errors: $ERRORS"

}

function start_gnome_term {

    echo "Starting terminal: $1"
    gnome-terminal --profile=${PROFILE} --geometry=${GEOMETRY_G} --hide-menubar -- tmux att -t $1:1

}

function start_x_term {

    echo "Starting terminal: $1"
    xfce4-terminal --geometry=${GEOMETRY_X} --hide-menubar --hide-toolbar -e "tmux att -t  $1:1"

}

function start_apple_term {

    echo "Starting terminal: $1"
    echo '..TBD'
    tmux att -t $SESS
}

function usage {

    echo "Usage: start_term.sh OPT"
    echo "       OPT: Env:  {-a,--apple,-g,--gnome,-x,--xorg}"
    echo "       OPT: Tmux: {-s,--sess,-p,--proj}" 
    exit 1

}


# Execute
unset SET_ENV
while [ "$#" -gt 0 ]; do
  # Start term in proper env
  case $1 in
  -a|--apple)
      echo "Setting Env: AppleOS"
      SET_ENV="apple"
      shift
      ;;
  -g|--gnome)
      echo "Setting Env: Gnome"
      SET_ENV="gnome"
      shift
      ;;
  -x|--xorg)
      echo "Setting Env: Xorg"
      SET_ENV="xorg"
      shift
      ;;
  -p|--proj)
      echo "Constructing project: $2"
      PROJ=$2
      shift
      shift
      ;;
  -s|--sess)
      echo "Setting session-name: $2"
      SESS=$2
      shift
      shift
      ;;
  *)  usage
      ;;
  esac
done

if [ -z $SET_ENV ]; then
  # Attempt Auto WM detection
  get_env
  if [ -z $SET_ENV ]; then
    echo "Unable to determine WM Env.  Please specify."
      usage
  fi
fi

# Build/Detect Tmux Session
get_tmux $SESS $PROJ &&\

# Launch terminal in respective env
case $SET_ENV in
  gnome)
    start_gnome_term $SESS
    ;;
  xorg)
    start_x_term $SESS
    ;;
  apple)
    start_apple_term $SESS
    ;;
esac
