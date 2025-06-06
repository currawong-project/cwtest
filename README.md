# cwtest Testing and Development Application for libcw.

`cwtest` is a command line interface to [`libcw`](https://github.com/currawong-project/libcw).
It is primarily used to as a minimal interface to develop and test `libcw` subsystems.

See the [Currawong audio processing language and environment `caw`](https://github.com/currawong-project/caw)
for an example of a complete application based on [`libcw`](https://github.com/currawong-project/libcw).

`cwtest` command line:
```
cwtest <file.cfg> <label>
```

Where `<file.cfg>` refers to a libcw configuration file file with the form:
```
{
  test: {
  
    `program_0`: {
      a:1
      b:"hello"
    },
    
    `program_1`: {
      arg0:["abc","def"]
      b:{ a:73, z:[19] }
    }
}
```

`<label>` refers to a specific set of named parameters
(e.g. `program_0`,`program_1`) which are associated with a library
function.  See `main.cpp` `mode_array[]` for the mapping of labels to
functions.

The goal of `cwtest` is to be able to easily exercise `libcw`
functions, or build simple utilities based on them, with a flexible
sets of parameters.  The primary parameter file used for the programs
and tests below is `src/cwtest/cfg/main.cfg`.

Below is a list of named parameter sets from `src/cwtest/cfg/main.cfg`.
The `label` field refers to the name given to a parameter set
in the `main.cfg` and is also used to select the associated program
from the command line utility.  Searching for the label in 'main.cfg'
will show the complete set of editable parameters available for a given
test function.

The `Source File` and `Function` field gives the source code
location for the function associated with each parameter set.

----

# MIDI - MIDI devices and files.


Label                 |      Source File     | Function     
----------------------|----------------------|--------------
__midiDeviceReport__  | cwMidiDeviceTest.cpp | testReport()

List The current set of MIDI hardware devices


Label             |      Source File     | Function     
------------------|----------------------|--------------
__midiDevice__    | cwMidiDeviceTest.cpp | test()

Interactive testing of the MIDI input file device
start/pause/unpause/stop functions.  This function also validates the
latency of the device by comparing the time between MIDI events as
generated by the device to the actual time between the events in the
MIDI file.


Label             |      Source File     | Function     
------------------|----------------------|--------------
__midifile__      | cwMidiFile.cpp       | test()

MIDI file utility parameters:

- Convert a MIDI file to a CSV file.
```
csv: { midiFn:<filename> csvFn:<filename> }
```

- Print the first <msgCnt> MIDI messages from a file.
```
rpt_beg_end: { midi_fname:<filenae>, msgCnt:<int>, note_on_only_fl:<true|false> }
```

- Print the entire contents of the MIDI file.
```
rpt : { midiFn:<filename> }
```

- Convert all the MIDI files in the folder: `<path>/<folder>/take/'record_%i'` to CSV files
```
batch_convert: { io_dir:<path>, session_dir:<folder>, take_begin:<int>, take_end:<int> print_warnings_flag:<true|false> }
```

----

## Serial - Serial Port Manager

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__serialSrv__     | cwSerialPortSrv.cpp  | sesrialPortSrvTest()

This is an interactive test of the serial port send/receive functions.
The function continuously transmits ASCII values '0' through 'z' to external devices `/dev/ttyACM0` and `/dev/ttyACM1`.
Those devices should increment the received value and send it back, where it is receieved and printed to the console.
Firmware to run on ATMEGA328 based devices, like the Arduino Uno, is provided in `study/serial/arduino_xmt_recv/main.c`.

----

## wesockSrv - Web Sockets Server

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__websockSrv__    | cwWebSockSvr.cpp     | websockSrvTest()


Interactive websocket server testing application.
Run the app and navigate in a web browser to `localhost:5687` to run the application.

----

## nbmpscQueue - Non-Blocking Multiple Producer Single Consumer Queue

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__nbmpscQueue__   | nbmpscQueue.cpp      | test()

Run the non-blocking, multiple producer, single consumer queue for 'testDurMs' millisecdons
and write the result into 'out_fname'.  This is the queue used by the websocket implementation
(See cwWebSock.h/cpp) to support incoming calls form multiple threads without blocking the calling threads.

----

# Audio

CLI Label         |      Source File      | Function     
------------------|-----------------------|---------------------
__audioDevTest__  | cwAudioDeviceTest.cpp | test()

Interactive testing of a specified audio device using the
cwAudioBuf functions: tones, pass-through, metering.
Use 'audioDevRpt' to get the possible labels for 'inDev' and 'outDev'.


CLI Label            |      Source File      | Function     
---------------------|-----------------------|---------------------
__audioDevFileTest__ | cwAudioDeviceFile.cpp | Test()

Test the input and output audio file device driver
by setting a input file to 'inAudioFname' and writing
the output file to 'outAudioFname'.  'cycleCnt'
is the total count of test audio cycles.


CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__audioDevRpt__   | cwAudioDevice.cpp    | report()

Generate a list of devices and device attributes from libcw.  This will include audio file based devices.

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__audiofile__     | cwAudioFile.cpp      | test()

Report the audio file format and a selected set of sample values.

# Operations on Audio Files

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__afop__          | cwAudioFileOps.cpp   | test()

sine - generate a sine signal
mix - mix multiple audio files with selectable gains per file.
select_to_file - save sections of audio files to new audio files
cutAndMix - Extract a section of source audio, apply fade in/out ramps, and mix it into a destination file.
parallelMix - Given a set of overlapping source files of identical length solo a given source during a specified time interval.
transformApp - Currawong online transform audition demo.
convolve - Convolve an audio file with an impulse response
generate - Synthesize a signal.

CLI Label            |      Source File     | Function     
---------------------|----------------------|---------------------
__audio_file_proc__  | cwAudioFileProc.cpp  | file_processor()

General purpose audio file processing pipeline.

CLI Label            |      Source File      | Function     
---------------------|-----------------------|---------------------
__pvoc_file_proc__   | cwPvAudioFileProc.cpp | pvoc_file_processor()

General purpose audio file processing for phase-vocoder based processing.


----

# Socket

CLI Label               |      Source File     | Function     
------------------------|----------------------|---------------------
__socketMgrSrvTest__    | cwSocket.cpp         | mainTest()
__socketMgrClientTest__ | cwSocket.cpp         | mainTest()

This is based on the current cwSocket implementation.
Interactive socket based client/server application.
Start `socketMgrSrvTest` in one process, then `socketMgrClientTest`
in a second processor.


CLI Label            |      Source File     | Function     
---------------------|----------------------|---------------------
__socketUdp__        | cwTcpSocketTest.cpp  | test_udp()

This is based on the cwTcpSocket implemetation, as developed for use with MDNS,DNSD,EUCON.
Interactive tester.

CLI Label            |      Source File     | Function     
---------------------|----------------------|---------------------
__socketTcpClient__  | cwTcpSocketTest.cpp  | test_tcp()
__socketTcpServer__  | cwTcpSocketTest.cpp  | test_tcp()

This is based on the cwTcpSocket implemetation, as developed for use with MDNS,DNSD,EUCON.
Interactive tester.

CLI Label            |      Source File     | Function     
---------------------|----------------------|---------------------
__socketSrvUdp__     | cwTcpSocketTest.cpp  | test_udp_srv()
__socketSrvTcp__     | cwTcpSocketTest.cpp  | test_tcp_srv()

This is based on the cwTcpSocket implemetation, as developed for use with MDNS,DNSD,EUCON.
Interactive tester.


CLI Label            |      Source File     | Function     
---------------------|----------------------|---------------------
__socketMdns__       | cwMdns.cpp           | test()

Runs a very specific test for simulating a Euphonix MC Mixer surface.


CLI Label            |      Source File     | Function     
---------------------|----------------------|---------------------
__dnssd__            | cwDnssd.cpp           | test()

Runs a very specific test for simulating a Euphonix MC Mix surface.


CLI Label            |      Source File     | Function     
---------------------|----------------------|---------------------
__eucon__            | cwEuCon.cpp           | test()

Runs a very specific test for simulating a Euphonix MC Mix surface.

----

# File system


CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__dirEntry__      | cwFileSys.cpp        | dirEntryTest()

Exercise the directory reader.

----

# IO Interface

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__io_minimal__    | cwIoMinTest.cpp      | min_test()

Incomplete minimal template for an application based on cwIo.h/cpp without a GUI.

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__io__            | cwIoTest.cpp         | test()

Incomplete but working interactive app used to test and develop cwIo based applications.


CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__audio_midi__    | cwIoAudioMidiApp.cpp | main()

Program for recording and playing back real-time Audio and MIDI.
Based on cwIoAudioRecordPlay and cwIoMidiRecordPlay.

----

# Dataset Related

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__mnist__         | cwDatasets.cpp       | mnist::test()

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__dataset_wtr__   | cwDatasets.cpp       | wtr::test()

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__dataset_rdr__   | cwDatasets.cpp       | rdr::test()

CLI Label          |      Source File     | Function     
-------------------|----------------------|---------------------
__dataset_adpter__ | cwDatasets.cpp       | adapter::test()

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__dataset__       | cwDatasets.cpp       | test()

Read MNIST native file -> write dataset file -> read datasetfile -> write SVG file

----

# SVG

CLI Label         |      Source File     | Function     
------------------|----------------------|---------------------
__svg__           | cwSvg.cpp            | test()

Test the SVG file writer.


## Run Unit Tests:

These test are run by the libcw testing framework in cwTest.h/cpp.
The configuraton for the unit tests is in `src/cwtest/src/cfg/test/main.cfg`.

1. Add a new test:
    - Create a function like this: rc_t my_test_func(const test_args_t& args);
    - Add the module name, function pair to the `_test_map[]` in cwTest.cpp.
    - Add an entry to the test parameters cfg. below.
        + Name the test case (e.g. `test_0`) and give the test parameters. 
        + On the call to my_test_func() the args.module_args is set to the 'module_args' dictionary defined in the cfg.
        + Likewise args.test_args is set to the 'test_args' dictionary referenced by the test name label 'e.g. test_0:{ my_arg:1 }'.
	  
    - Run the test like this: `cwtest test/main.cfg test /my_module test_0 echo` to see the results of the test run.
      The results of this run will be written into `/cur/my_test/test_0/log.txt`
  
    - Once the results have been validated copy the output from 'cur' to the `/ref/my_test/test_0/log.txt.`
    
    - Verify that the test passes: `cwtest test/main.cfg test /my_module test_0 compare`


2. The test spec. is recursive. Modules can be listed inside of modules.  (e.g. 'lex' and 'flow').

3. If a module spec. does not have an embedded
      'module' or 'module_args' then the cases may
      be listed without a 'cases' label.
      (e.g. 'filesys','object', 'vop')
    
4. Command line args:

      Parameter     |  Description
    ----------------|------------------------------------------------------------------
      <module_path> | 'all'  (required) The module path always begins with a '/'.
      <test_label>  | 'all'  (required)
      'gen_report'  | Print modulue/test label.
      'compare'     | Run compare pass.
      'echo'        | Print the generated test output to the console.
      'args'        | All command line args after 'args' are passed to the tests.
    
5. Example command lines:
```
      cwtest ~/src/cwtest/src/cwtest/cfg/test/main.cfg test /lex test_0 gen
      cwtest ~/src/cwtest/src/cwtest/cfg/test/main.cfg test /flow test_0 compare
```



# GDB Setup:

    set env LD_LIBRARY_PATH /home/kevin/src/libcm/build/linux/debug/lib
    r ~/src/cwtest/src/cwtest/cfg/main.cfg mtx

    // if problems occur with gdb hanging while download debuginfo 
    sudo dnf upgrade --enablerepo=*-debuginfo "*-debuginfo"   # update all debuginfo files

    r ~/src/cwtest/src/cwtest/cfg/video/video.cfg preset_sel  record_fn m302-325 beg_play_loc 9187 end_play_loc 10109
    r ~/src/cwtest/src/cwtest/cfg/video/video.cfg preset_sel  record_fn m350-458 beg_play_loc 12431 end_play_loc 14726
    r ~/src/cwtest/src/cwtest/cfg/video/video.cfg preset_sel  record_fn m1_283 beg_play_loc 0 end_play_loc 8452
    
    r ~/src/cwtest/src/cwtest/cfg/gutim_full/gutim.cfg preset_sel  record_fn m1_458 beg_play_loc 327 end_play_loc 396
	
	
     
# Valgrind setup

    export LD_LIBRARY_PATH=~/src/libcm/build/linux/debug/lib
    valgrind --leak-check=yes --log-file=vg0.txt ./cwtest  ~/src/cwtest/src/cwtest/cfg/main.cfg mtx
	
# Installation

Dependencies:

- libwebsockets-devel
- fftw-devel
- libcm: lapack-devel
-       atlas-devel

#Design Questions:

How should errors be presented to the user? developer?


#To Do:

### 

All callbacks should return meaningful result codes.


### UI Properties

    name            - becomes the HTML id for this element
    appId             application id for this element
    title             label or title for this element
    className         Base class name for this element. All elements have a built-in default class name.
    addClassName      Add this class name to the class name.
    clickable         This elemnt will send a 'click' msg when clicked.
    enable            This element is enabled
    visible           This element is visible.

# Preset Select
   
+ If the the parsing of the main cfg file fails the app crashes in main.cpp with a double free.
+ play on preset letter select
+ allow the network to be reloaded without restarting the program
+ create an interactive spec-dist panel to experiment with presets


REVIEW:
+ gain problem
- was it really the transition bug and not a gain bug?
- FFT normalization
- Float/Int conversion on ALSA output
- create a metering object to examine signal at various places in network
- add compressor/limiter like in cm based network



DONE:
+ save preset check box state.
+ verify that all fragments are saved and restored
+ UI:         remove 'Filename' entry box.
+ flow proc:  gain, audio channel split map, audio channel merge map, fixed delay 
+ Fix CPU usage: work around for serial port server.
+ App:        apply wet/dry and gain when new presets are loaded.
+ App:        add 'Note' to fragment 
+ App:        add per fragment play control with begin/end locations
+ UI:         reorganinze top panel layout
+ App:        Add a status box to report errors and warnings to the user.
+ App:        Send log output to "Log" UI.
+ App:        When a invalid value is entered (thereby disabling a control) a message should be written to the status box.
+ App:        Add ranges to numeric controls.
+ App:        What happens when an invalid value is entered in a GUI control?
+ App:        interactive wet in gain, wet out gain, dry gain, piano midi enable, sampler midi enable, sampler delay
+ App:        interactive print network
+ App:        automatically load on start
+ flow:       Allow setting a specific variable value from a network preset
+ preset_sel: The sampler requires a different velocity map than the piano. The piano was scaled down but now the sampler is too quiet.
+ preset_set: deleting a fragment does not automatically fill in the missing location space.
+ preset_sel: backup to numbered file on save
+ preset_sel: Velocity of the individual notes of chords should be scaled to such that their sum matches the dynamic value.
+ libcw:      Make IO sub-systems optionally synchronous
+ UI:         clear UI when the app disconnects.
+ UI: Add an error indicator and API for each control (e.g. border set to red)
+ UI: Add the ability to order child lists via the 'order' attribute.
+ UI: Add API to delete a UI element
+ UI: add HTML class and name assignments to row/col div's.  (See 'name' and 'addClassName' attribute.)
+ UI: add min/max/incr/decpl attributes to numeric variables (See uiSetNumbRange.)

+ PresetSel: Select and highlight a fragment.
+ PresetSel: + test adding,deleting, saving and restoring fragment records
+ Enable 'Delete' button when a fragment is selected.
