# export LD_LIBRARY_PATH=~/sdk/libwebsockets/build/out/lib
valgrind --leak-check=yes --log-file=vg0.txt --track-origins=yes bin/cwtest ../../../src/cwtest/cfg/main.cfg $1

