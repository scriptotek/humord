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

#==========================================================
# Publish compressed dumps
#==========================================================

DUMPS_DIR=/projects/data.ub.uio.no/dumps

cp HUMEregister.ttl humord.ttl
bzip2 -k humord.ttl
zip humord.ttl.zip humord.ttl
cp humord.ttl.zip $DUMPS_DIR/
cp humord.ttl.bz2 $DUMPS_DIR/
rm *.bz2 *.zip
rm humord.ttl

