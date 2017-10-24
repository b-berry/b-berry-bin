#!/bin/bash

GEOMETRY_G='155x45+88+68'
GEOMETRY_X='155x45+35+50'
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

function get_env {

    unset E_STATUS
    printf 'Detecting WM Env: '
    if [[ ( ! -z $XDG_CURRENT_DESKTOP ) || ( ! -z $GDMSESSION ) ]]; then
        printf 'OK\n  Desktop: %s\n  Session: %s\n' "$XDG_CURRENT_DESKTOP" "$GDMSESSION"
        E_STATUS=0
        WM=$GDMSESSION
        return 
    else
        printf 'ERROR'
        E_STATUS=1
    fi

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
    gnome-terminal --profile=${PROFILE} --geometry=${GEOMETRY_G} -- tmux att -t $1:1

}

function start_x_term {

    echo "Starting terminal: $1"
    xfce4-terminal --geometry=${GEOMETRY_X} --hide-menubar --hide-toolbar -e "tmux att -t  $1:1"

}

function usage {

    echo "Usage: start_term.sh OPT"
    echo "       OPT: {-g,--gnome,-x,--xorg}"

}


# Execute
if [ -z $1 ]; then
    # Attempt Auto WM detection
    get_env
    if [ $E_STATUS -gt 0 ]; then
        echo "Unable to determine WM Env.  Please specify."
        usage
    else

        get_tmux $SESS 

        case $WM in
        gnome)
            start_gnome_term $SESS
            ;;
        xorg)
            start_x_term $SESS
            ;;
        esac
    fi
else
    # Start term in proper env
    case $1 in
    -g|--gnome)
        echo "Getting tmux"
        get_tmux $SESS
        start_gnome_term $SESS
         ;;
    -x|--xorg)
        echo "Getting tmux"
        get_tmux $SESS
        start_x_term $SESS
        ;;
    *)  usage
        ;;
    esac
fi
