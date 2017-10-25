#!/bin/bash

# Using john the ripper to brute-force a luks container
# Run as root

startTime=$(date)

if [ $(cryptsetup luksDump $1 | grep -c "LUKS header information") ]; then
    john -i --stdout | while read i; do
        echo -ne "\rtrying \"$i\" "\\r
        echo $i | cryptsetup luksOpen $1 x --test-passphrase -T1 2> /dev/null
        STATUS=$?
        if [ $STATUS -eq 0 ]; then
            echo -e "\nPassword is: \"$i\""
            break
         fi
    done

    echo "Start time $startTime"
    echo "End time $(date)"

else

    echo "The file does not appear to be a LUKS encrypted file"

fi
