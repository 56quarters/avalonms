#!/bin/sh

cd
rm -rf avalon
virtualenv avalon
source avalon/bin/activate
pip install -e git+https://github.com/tshlabs/avalonms.git#egg=avalonms
avalonmsd ~/music
