#!/bin/bash

curl -L -o iprad.zip https://github.com/deltaaa00/iprad/archive/refs/heads/main.zip


HASH_FILE="$HOME/iprad.hash"


if command -v sha256sum >/dev/null; then
    NEW_HASH=$(sha256sum iprad.zip | awk '{ print $1 }')
else
    NEW_HASH=$(shasum -a 256 iprad.zip | awk '{ print $1 }')
fi


if [ -f "$HASH_FILE" ]; then
    OLD_HASH=$(cat "$HASH_FILE")

 
    if [ "$NEW_HASH" == "$OLD_HASH" ]; then
        echo "You have the latest version"
        rm iprad.zip
        exit 0
    fi
fi


echo "$NEW_HASH" > "$HASH_FILE"


unzip iprad.zip || exit


cd iprad-main || exit

pip3 install -e .

cd ..

clear
rm iprad.zip
echo "Install finished. Press enter to exit"
read