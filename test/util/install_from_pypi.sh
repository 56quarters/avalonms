#!/bin/sh

cd
rm -rf avalon
virtualenv avalon
source avalon/bin/activate
pip install avalonms
avalonmsd ~/music

