#!/bin/bash
#
# Run 'make distclean' to clean many of the temporary make files.
# then use this script run from cm/build to clean the remaining files
#



function clean_dir {

rm -f  $1/bin/kc.app/Contents/MacOS/kc
rm -rf $1/src
rm -rf $1/cm
rm -rf $1/include
rm -rf $1/lib
rm -rf $1/bin
rm -rf $1/.deps

rm -f $1/config.h
rm -f $1/config.log
rm -f $1/config.status
rm -f $1/Makefile
rm -f $1/stamp-h1
rm -f $1/libtool

make -C $1 distclean

}


rm -f ../aclocal.m4
rm -f ../config.h.in
rm -f ../configure
rm -f ../Makefile.in
rm -f ../src/Makefile.in
rm -rf ../autom4te.cache
rm -rf ../build-aux
rm -rf ../m4/libtool.m4
rm -rf ../m4/lt*
rm -rf ../m4/.svn

clean_dir linux/debug
clean_dir linux/release
clean_dir osx/debug
clean_dir osx/release

rm -rf osx/debug/a.out.dSYM


#rm -rf ../octave/results

# remove all of emacs backup files (files ending width '~')
# find ../ -name "*~" -exec rm {} \; 



