#!/bin/bash

OathFile="/tmp/.CopyPasteFireToken";


function verify_user(){
    identifier=$(blkid | grep -oP 'UUID="\K[^"]+' | echo "$(cat)$RANDOM" | cksum | awk '{print $1}');
    printf "please go to\n \033[0;34m  https://copy-passed.web.app/VerifyID.html#$identifier  \033[0m  \nto complete the signin\n";
    output=$(curl -f -s -d '{"id":"'$identifier'"}' -H "Content-Type: application/json" -X POST https://us-central1-copy-passed.cloudfunctions.net/authenticator)
    status=$?
    if [ 0 -eq $status ]
    then
        key=$(echo $output | sed -n 's|.*"id":"\([^"]*\)".*|\1|p');
        #echo $output $key;
        echo $key > $OathFile
        return;
    else
        echo "$status error retying..."
        verify_user;
    fi
}


while getopts ":r" opt; do
  case $opt in
    r)
      verify_user
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done


oToken=$(cat $OathFile);


if [ -z "$oToken" ]
then
    verify_user;
fi



if [ -p /dev/stdin ]
then
    input=$(cat | sed 's/\\/\\\\/g' | sed 's/\x22/\\\x22/g');
    payload=$(echo '{"id":"'$oToken'","method":"post","data":'$(printf "\x22$(echo $input | sed 's/\\/\\\\/g')\x22")'}');
    #echo $payload
    dump=$(echo "curl -s -f -d $(printf "\x27$(echo $payload  | sed 's/\\/\\\\/g')\x27") -H 'Content-Type: application/json' -X POST https://us-central1-copy-passed.cloudfunctions.net/access");
    eval $dump
    #echo $?
else
    output=$(curl -s -f -d '{"id":'$(echo \"$oToken\")',"method":"get"}' -H "Content-Type: application/json" -X POST https://us-central1-copy-passed.cloudfunctions.net/access);
    echo $(echo $output | sed -n 's|.*"last":"\([^"]*\)".*|\1|p')
fi
