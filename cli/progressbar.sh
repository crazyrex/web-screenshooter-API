#!/usr/bin/env bash

#https://stackoverflow.com/questions/238073/how-to-add-a-progress-bar-to-a-shell-script#answer-31125424

preparebar() {
# $1 - bar length
# $2 - bar char
    barlen=$1
    barspaces=$(printf "%*s" "$1")
    barchars=$(printf "%*s" "$1" | tr ' ' "$2")
}

progressbar() {
# $1 - number (-1 for clearing the bar)
# $2 - max number
    if [ $1 -eq -1 ]; then
        printf "\r  $barspaces\r"
    else
        barch=$(($1*barlen/$2))
        barsp=$((barlen-barch))
        printf "\r[%.${barch}s%.${barsp}s]\r" "$barchars" "$barspaces"
    fi
}

