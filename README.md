This file is to be updated after the project is completed. For now, it is used as to-do list.

# Dependencies:
dbus-python
dconf (it most likely comes with your distro)

# file structure
run.py to be run as service
mountInfoHandler.js to be placed in ~/.local/share/gnome-shell/extensions/gsconnect@andyholmes.github.io/service/utils/




sftp.js either entirely replaced with existing or edit the existing one in `~/.local/share/gnome-shell/extensions/gsconnect@andyholmes.github.io/service/plugins/`
you can search for `this block of code is not part of gsconnect connect extension` to find the block of code that is added by this script
if script is editing the file, don't forget to place {} around else