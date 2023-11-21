
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import os
from urllib.parse import unquote
import subprocess

previous_locations = []

def gsconnectMount():
    return os.path.join(os.environ['HOME'], '.gsconnectMounts')

def mount_port(id):
    # dconf read /org/gnome/shell/extensions/gsconnect/device/DEVICE_ID/mount-port
    return subprocess.check_output(['dconf', 'read', f'/org/gnome/shell/extensions/gsconnect/device/{id}/mount-port']).decode('utf-8').strip()

def string_to_array(string):
    #string to array of strings
    string = string.strip()
    string = string[1:-1]
    string = string.split(',')
    string = [x.strip() for x in string]
    string = [x[1:-1] for x in string]
    return string
def multi_paths(id):
    # dconf read /org/gnome/shell/extensions/gsconnect/device/DEVICE_ID/multi-paths
    return string_to_array(subprocess.check_output(['dconf', 'read', f'/org/gnome/shell/extensions/gsconnect/device/{id}/multi-paths']).decode('utf-8'))
def path_names(id):
    # dconf read /org/gnome/shell/extensions/gsconnect/device/DEVICE_ID/path-names
    return string_to_array(subprocess.check_output(['dconf', 'read', f'/org/gnome/shell/extensions/gsconnect/device/{id}/path-names']).decode('utf-8'))
def last_connection(id):
    data = subprocess.check_output(['dconf', 'read', f'/org/gnome/shell/extensions/gsconnect/device/{id}/last-connection']).decode('utf-8')[1:-1]
    # 'lan://192.168.0.5:1716'
    return data[6:].split(':')[0]


def handle_signal(*args,**kwargs):
    global previous_locations
    open_locations = []
    for arg in args:
        if isinstance(arg, dbus.Dictionary):
            for key, value in arg.items():
                if key == 'OpenWindowsWithLocations':
                    for window, locations in value.items():
                        for location in locations:
                            open_locations.append(location)
    for location in open_locations:
        if location.startswith(f"file://{gsconnectMount()}"):
            if location in previous_locations:
                previous_locations.remove(location)
                continue
            handle_open_location(location)
    previous_locations = open_locations

def handle_open_location(location):
    if location == f"file://{gsconnectMount()}":
        return
    location = location[len(f"file://{gsconnectMount()}")+1:]
    location = location.split('/')
    if len(location) == 1:
        return
    name_of_device = unquote(location[0].split('___')[0])
    id_of_device = location[0].split('___')[1]
    location = unquote(location[-1])
    mapping = dict(zip(path_names(id_of_device), multi_paths(id_of_device)))
    mount_port_ = mount_port(id_of_device)
    last_connection_ = last_connection(id_of_device)
    os.system(f"nautilus sftp://{last_connection_}:{mount_port_}{mapping[location]} > /dev/null 2>&1 &")
def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)   
    bus = dbus.SessionBus()
    bus.add_signal_receiver(handle_signal,
                            dbus_interface='org.freedesktop.DBus.Properties',
                            signal_name='PropertiesChanged',
                            path='/org/freedesktop/FileManager1')
    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()