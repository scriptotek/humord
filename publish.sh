#!/bin/sh

git checkout master
git pull origin master

xc=$?
if [ $xc != 0 ]; then

    echo
    echo -----------------------------------------------------------
    echo ERROR:
    echo Could not git pull. Conflict?
    echo -----------------------------------------------------------
    exit 1

fi

make clean
make all

xc=$?
if [ $xc != 0 ]; then

    echo
    echo -----------------------------------------------------------
    echo ERROR:
    echo Make failed
    echo -----------------------------------------------------------
    exit 1

fi

git add HUMEregister.xml HUMEregister.ttl
git commit -m "Humord oppdatert fra Bibsys"
git push origin master


