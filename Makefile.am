ACLOCAL_AMFLAGS = -I m4 # use custom macro's in ./m4 
lib_LTLIBRARIES =
bin_PROGRAMS    =
include_HEADERS =



# C compiler flags
# _GNU_SOURCE - turns on GNU specific extensions and gives correct prototype for double log2(double) 
# -Wall turn on all warnings
# -Wno-multichar - turns off multi-character constant warnings from cmAudioFile.c



AM_CPPFLAGS = -D _GNU_SOURCE  -I.. 
AM_CFLAGS   = -Wno-multichar 
AM_CXXFLAGS = 
AM_LDFLAGS  =  

# debug/release switches
if DEBUG
  AM_CFLAGS   += -g 
  AM_CXXFLAGS += -g
else
  AM_CFLAGS   += -O3
  AM_CXXFLAGS += -O3
endif

# Linux specific
if OS_LINUX

if OS_64
  AM_CFLAGS  += -m64
endif	
endif



include src/libproj/Makefile.am


src_libproj_libproj_la_SOURCES = $(libprojSRC) $(libprojHDR)
lib_LTLIBRARIES               += src/libproj/libproj.la
include_HEADERS               += $(libprojHDR)


src_proj_proj_SOURCES   = src/proj/main.c
src_proj_proj_LDADD     = src/libproj/libproj.la  # autoconfig manual recommends setting direct referenes to non-3rd party libraries rather than using -L and -l
src_proj_proj_CPPFLAGS  = -I$(srcdir)/src/libproj $(AM_CPPFLAGS)
bin_PROGRAMS           += src/proj/proj
