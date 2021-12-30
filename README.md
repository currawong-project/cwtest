libcw Testing and Development App

# GDB Setup:

    set env LD_LIBRARY_PATH /home/kevin/sdk/libwebsockets/build/out/lib
    r ~/src/cwtest/src/cwtest/cfg/main.cfg mtx


# Valgrind setup

    export LD_LIBRARY_PATH=~/sdk/libwebsockets/build/out/lib
    valgrind --leak-check=yes --log-file=vg0.txt ./cwtest  ~/src/cwtest/src/cwtest/cfg/main.cfg mtx

#Design Questions:

How should errors be presented to the user? developer?


#To Do:

### 

All callbacks should return meaningful result codes.

### uiTest:

- Fix crash when '=' is used as a pair separator rather than ':'.
cwUi is not noticing when a UI resource file fails to parse correctly.
This may be a problem in cwObject or in cwUI.

- Fix bug where leaving out the ending bracket for the first 'row' div in ui.cfg
causes the next row to be included in the first row, and no error to be generated,
even though the resource object is invalid (i.e. there is a missing brace).

- Document the UI client/server protocol.
1. The message formats to and from the server and the javascript client.
2. When the messages are sent.

- UI: Document the UI resource file format.

- UI: Add support for custom controls.

- UI: Add an option to print the UI elment information as they are created.
This is a useful way to see if id maps are working.
Print: ele name, uuid, appId and parent name, uuid, appId

- UI: Add an error indicator and API for each control (e.g. border set to red)
- UI: Add the ability to order child lists via the 'order' attribute.
- UI: Add API to delete a UI element

- PresetSel: Select and highlight a fragment.
- Enable 'Delete' button when a fragment is selected.




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

- Test:
   audio_split
   audio_merge
   audio_mix
   audio_delay
   balance
   

- Functionality
+ create a wrappers for all the cm based procs.
+ UI:         clear UI when the app disconnects.
+ App:        automatically load on start
+ object       Improve performance of load parser.
+ App:         Add input / output metering

+ flow:       allow setting a specific variable value from a network preset
+ flow:       create default system wide sample rate
+ UI          uiSetValue() should be optionally reflected back to the app with kValueOpId messages.
              This way all value change messages could be handled from one place no matter
			  if the value changes originate on the GUI or from the app.
			  
+ IO threading
+ document basic functionality: flow, UI, Audio
+ Using the 'blob' functionality should be the default way for tying UI elements to program model.
  Rewrite the UI test case to reflect this.

+ breakout libcw from application / reorganize project
+ create true plug-in architecture - requires a C only interface.



- Add attributes to proc variables:
  1. 'init' this variable is only used to initialize the proc. It cannot be changed during runtime.  (e.g. audio_split.map)
  2. 'scalar' this variable may only be a scalar.  It can never be placed in a list.  (e.g. sine_tone.chCnt)
  3. 'multi' this src variable can be repeated and it's label is always suffixed with an integer. 
  4. 'src' this variable must be connected to a source.
  5. 'min','max' for numeric variables.
  6. 'channelize' The proc should instantiate one internal process for each input channel. (e.g. spec_dist )
  
- Create a var args version of 'var_get()' in cwFlowTypes.h.

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
