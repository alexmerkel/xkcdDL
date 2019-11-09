#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: xkcdMissing FROM TO"
fi

seq "$1" "$2" | while read -r i; do
    if [ ! -f "$i.json" ]; then
        echo "JSON missing for #$i"
    fi
    if [ ! -f "$i.png" ] && [ ! -f "$i.jpg" ] && [ ! -f "$i.gif" ]; then
        echo "Image missing for #$i"
    fi
done

