ACLOCAL_AMFLAGS = -I m4 # use custom macro's in ./m4 
lib_LTLIBRARIES =
bin_PROGRAMS    =
include_HEADERS =

# To Profile w/ gprof:
# 1) Modify configure: ./configure --disable-shared CFLAGS="-pg"
# 2) Run the program. ./foo
# 3) Run gprof /libtool --mode=execute gprof ./foo

# C compiler flags
# _GNU_SOURCE - turns on GNU specific extensions and gives correct prototype for double log2(double) 
# -Wall turn on all warnings
# -Wno-multichar - turns off multi-character constant warnings from cmAudioFile.c


WS_DIR   = $(HOME)/sdk/libwebsockets/build/out


AM_CPPFLAGS = -D _GNU_SOURCE  -I..  -I$(srcdir)/src/libcw
AM_CFLAGS   = -Wno-multichar 
AM_CXXFLAGS = -Wno-multichar
AM_LDFLAGS  =  

# debug/release switches
if DEBUG
  AM_CFLAGS   += -g 
  AM_CXXFLAGS += -g -Wall 
else
  AM_CFLAGS   += -O3
  AM_CXXFLAGS += -O3
endif

# Linux specific
if OS_LINUX

if OS_64
  AM_LDFLAGS +=  -L/usr/lib64
  AM_CFLAGS  += -m64
endif

if cwALSA
  AM_LDFLAGS +=    -Wl,-Bstatic -lasound -Wl,-Bdynamic
endif

endif

include src/libcw/Makefile.am

libcw_la_SOURCES  = $(libcwSRC) $(libcwHDR)
lib_LTLIBRARIES  += libcw.la 
include_HEADERS  += $(libcwHDR)


src_cwtest_cwtest_SOURCES   = src/cwtest/main.cpp

# 1) autoconfig manual recommends setting direct referenes to non-3rd party libraries rather than using -L and -l
# 2) -ldl is required for dlopen(),dlclose() ...
src_cwtest_cwtest_LDADD     = libcw.la  -lpthread -ldl -lfftw3 -lfftw3f

if cwWEBSOCK
  AM_CPPFLAGS += -I$(WS_DIR)/include
  AM_LDFLAGS  += -L$(WS_DIR)/lib
  src_cwtest_cwtest_LDADD +=  -lwebsockets
endif


# src_cwtest_cwtest_CPPFLAGS  = -I$(srcdir)/src/libcw $(AM_CPPFLAGS)
bin_PROGRAMS               += src/cwtest/cwtest
