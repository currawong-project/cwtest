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

- Add a status box to report errors and warnings to the user.
- When a invalid value is entered (thereby disabling a control) a message should be written to the status box.
