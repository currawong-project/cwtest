libcw Testing and Development App

#Design Questions:

How should errors be presented to the user? developer?


#To Do:

### 

All callbacks should return meaningful result codes.

### uiTest:

Fix crash when '=' is used as a pair separator rather than ':'.
cwUi is not noticing when a UI resource file fails to parse correctly.
This may be a problem in cwObject or in cwUI.

Fix bug where leaving out the ending bracket for the first 'row' div in ui.cfg
causes the next row to be included in the first row, and no error to be generated,
even though the resource object is invalid (i.e. there is a missing brace).

Document the UI client/server protocol.
1. The message formats to and from the server and the javascript client.
2. When the messages are sent.

Document the UI resource file format.

Add support for custom controls.

Add an option to print the UI elment information as they are created.
This is a useful way to see if id maps are working.
Print: ele name, uuid, appId and parent name, uuid, appId


# GDB Setup:

`set env LD_LIBRARY_PATH /home/kevin/sdk/libwebsockets/build/out/lib`
`r ~/src/cwtest/src/cwtest/cfg/main.cfg mtx`


# Valgrind setup

`export LD_LIBRARY_PATH=~/sdk/libwebsockets/build/out/lib`
`valgrind --leak-check=yes --log-file=vg0.txt ./cwtest  ~/src/cwtest/src/cwtest/cfg/main.cfg mtx`
