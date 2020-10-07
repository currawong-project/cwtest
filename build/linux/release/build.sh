#!/bin/sh

curdir=`pwd`

cd ../../..
autoreconf --force --install

cd ${curdir}

../../../configure --prefix=${curdir} --enable-websock --enable-alsa \
CFLAGS="-Wall" \
CXXFLAGS="-Wall" \
CPPFLAGS="-I${HOME}/sdk/libwebsockets/build/out/include" \
LDFLAGS="-L${HOME}/sdk/libwebsockets/build/out/lib" \
LIBS=


#make
#make install
