#!/bin/sh

curdir=`pwd`

cd ../../..
autoreconf --force --install

cd ${curdir}

../../../configure --prefix=${curdir} --enable-websock --enable-alsa \
CFLAGS="-Wall" \
CXXFLAGS="-Wall" \
CPPFLAGS="-I${HOME}/src/libcm/build/linux/release/include" \
LDFLAGS="-L${HOME}/src/libcm/build/linux/release/lib" \
LIBS=


#make
#make install
