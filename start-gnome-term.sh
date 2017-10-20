#!/bin/bash

GEOMETRY='155x45+88+68'
PROFILE='default'
SESS='desktop'

function build_tmux {

    STATUS=0
    T_SESS=$1

    # Set up window names : => dir
    declare -a conf_tmux=('me' 'far' '2' ':src' ':lg-chef' '5')

    first=true
    for n in $(seq 0 $(echo "${#conf_tmux[@]}-1" | bc)); do
        INSTANCE=${conf_tmux[$n]}
	    echo $INSTANCE
	    # Sort item type
        if [[ $INSTANCE == *":"* ]]; then
            NAME="${INSTANCE#*:}"
            DIR=$(find $HOME/* -type d -name $NAME)
            # Correct dir if not found
            if [ ! -d $DIR ]; then
                DIR=$HOME
            fi
        else
            NAME=${conf_tmux[$n]}
            DIR=$HOME
        fi
        # If first create session
        if $first; then
            echo "Initiating tmux session: $T_SESS:$NAME"
            tmux new-sess -d -s $T_SESS -n $NAME
            T_STATUS=$?
            if [ $T_STATUS -lt 1 ]; then
                first=false
                continue
            fi
        fi
        # Build item in tmux
        printf "Building tmux new-window $NAME:$DIR "
        tmux new-window -d -c $DIR -n $NAME -t $T_SESS
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

function get_tmux {

    # Set up or join exiting tmux env
    tmux has-sess -t $1
    T_STATUS=$?
    if [ $T_STATUS -gt 0 ]; then
       # Create session
       echo "No tmux:$1 found... initiating"
       build_tmux $1
    else
       echo "Found exiting tmux: $1" 
       return       
    fi 

}

function report_error {

    ERRORS=$1
    echo "Encountered errors: $ERRORS"

}

function start_term {

    echo "Starting terminal: $1"
    gnome-terminal --profile=${PROFILE} --geometry=${GEOMETRY} --hide-menubar -- tmux att -t $1:1

}

# Execute
echo "Getting tmux"
get_tmux $SESS
echo "Starting term"
start_term $SESS
