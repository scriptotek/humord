#!/bin/sh

function install_deps
{
    echo Installing/updating dependencies
    pip install -U git+git://github.com/danmichaelo/skosify.git
    xc=$?

    if [ $xc != 0 ]; then
        echo
        echo -----------------------------------------------------------
        echo ERROR:
        echo Could not install dependencies using pip
        echo -----------------------------------------------------------
        exit 1
    fi
}

cd ..

if [ ! -f ENV/bin/activate ]; then

    echo
    echo -----------------------------------------------------------
    echo Virtualenv not found. Trying to set up
    echo -----------------------------------------------------------
    echo
    virtualenv ENV
    xc=$?

    if [ $xc != 0 ]; then
        echo
        echo -----------------------------------------------------------
        echo ERROR:
        echo Virtualenv exited with code $xc.
        echo You may need to install or configure it.
        echo -----------------------------------------------------------
        exit 1
    fi

    echo Activating virtualenv
    . ENV/bin/activate

    install_deps

else

    echo Activating virtualenv
    . ENV/bin/activate

fi

cd humord


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

git add HUMEregister.xml HUMEregister.ttl skosify.log
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

