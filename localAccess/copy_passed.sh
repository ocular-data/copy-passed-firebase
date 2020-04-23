#!/bin/bash

OathFile="/tmp/.CopyPasteFireToken"

function verify_user() {
  identifier=$(blkid | grep -oP 'UUID="\K[^"]+' | echo "$(cat)$RANDOM" | cksum | awk '{print $1}')
  printf "please go to\n \033[0;34m  https://copy-passed.web.app/VerifyID.html#%s \033[0m  \nto complete the signin\n" "$identifier"
  output=$(curl -f -s -d '{"id":"'"$identifier"'"}' -H "Content-Type: application/json" -X POST https://us-central1-copy-passed.cloudfunctions.net/authenticator)
  status=$?
  if [ 0 -eq $status ]; then
    key=$(echo "$output" | sed -n 's|.*"id":"\([^"]*\)".*|\1|p')
    #echo $output $key;
    echo "$key" >$OathFile
    return
  else
    echo "$status error retying..."
    verify_user
  fi
}

while getopts ":r" opt; do
  case $opt in
  r)
    output=$(curl -f -s -d '{"id":"'"$(cat $OathFile)"'","revoke":true}' -H "Content-Type: application/json" -X POST https://us-central1-copy-passed.cloudfunctions.net/authenticator)
    verify_user
    ;;
  \?)
    echo "Invalid option: -$OPTARG" >&2
    ;;
  esac
done

oToken=$(cat $OathFile)

if [ -z "$oToken" ]; then
  verify_user
else
  output=$(curl -s -f -d '{"id":"'"$oToken"'","method":"get"}' -H "Content-Type: application/json" -X POST https://us-central1-copy-passed.cloudfunctions.net/access)
  status=$?
  if [ 0 -ne $status ]; then
    rm $OathFile
    verify_user
  fi

fi

oToken=$(cat $OathFile)

if [ -p /dev/stdin ]; then
  input=$(cat | sed 's/\\/\\\\/g' | sed 's/\x22/\\\x22/g' | sed ':a;N;$!ba;s/\n/\\n/g')
  payload='{"id":"'"$oToken"'","method":"post","data":'"$(printf "\x22%s\x22" "${input//\/\\/}")"'}'
  #echo $payload
  dump="curl -f -s -d $(printf "\x27%s\x27" "${payload//\/\\/}") -H 'Content-Type: application/json' -X POST https://us-central1-copy-passed.cloudfunctions.net/access"
  eval "$dump"
  #echo $?
  #echo "$dump";
else
  if [[ 0 -ne $status ]]; then
    output=$(curl -s -f -d '{"id":"'"$oToken"'","method":"get"}' -H "Content-Type: application/json" -X POST https://us-central1-copy-passed.cloudfunctions.net/access)
  fi
  echo -e "$(echo "$output" | perl -ne 'print /"last":"(.*)(?<!\\)"/s' | sed 's/\\\x22/\\x22/g')"
  #| sed 's|.*"last":"\([^"]*\)".*|\1|g')"
fi
