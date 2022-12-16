#!/bin/sh

curdir=`pwd`

cd ../../..
autoreconf --force --install

cd ${curdir}

../../../configure --prefix=${curdir} --enable-websock --enable-alsa \
CFLAGS="-Wall" \
CXXFLAGS="-Wall" \
CPPFLAGS="-I${HOME}/src/libcm/build/linux/debug/include" \
LDFLAGS="-L${HOME}/src/libcm/build/linux/debug/lib" \
LIBS=


#make
#make install
