libcw Testing and Development App


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
