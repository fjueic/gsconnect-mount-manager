#!/usr/bin/env python3

import sys

args = sys.argv
home = args[1]
extension_dir = args[2]


def change_sftp():
    # ~/.local/share/gnome-shell/extensions/gsconnect@andyholmes.github.io/service/plugins/sftp.js
    # extension_dir contains the home directory, so don't need to use os.path.join
    with open(
        f"{extension_dir}/plugins/sftp.js",
        "r+",
    ) as f:
        data = f.read()
        data = addMountingLogic(data)
        data = addunMountingLogic(data)
        f.seek(0)
        f.write(data)

def addMountingLogic(data):
    lines = data.split("\n")
    for i in range(len(lines)):
        if "else" in lines[i] and "this._handleMount(packet)" in lines[i + 1]:
            lines[
                i
            ] = """              else{ // if script is editing the file, don't forget to place {} around else
                        this._handleMount(packet);
                        let temp = JSON.stringify(packet);
                        let open = Gio.File.new_for_path(`${GLib.get_home_dir()}/.config/gsconnect-mount-manager/temp.json`);
                        let out = open.replace(null, false, Gio.FileCreateFlags.NONE, null, null);
                        out.write(temp, null);
                        out.close(null);
                        GLib.spawn_command_line_sync(`python3 ${GLib.get_home_dir()}/.config/gsconnect-mount-manager/mount.py add`)
                    }"""
            lines[i + 1] = ""
            break
    data = "\n".join(lines)
    return data


def addunMountingLogic(data):
    lines = data.split("\n")
    for i in range(len(lines)):
        if "_onMountRemoved(monitor" in lines[i]:
            lines[i] = (
                lines[i]
                + """
        // this block of code is not part of gsconnect connect extension
        try{
            GLib.spawn_command_line_sync(`python3 ${GLib.get_home_dir()}/.config/gsconnect-mount-manager/mount.py remove ${this._device._id}/`)

        }catch(e){
            pass
        }
        // end of block"""
            )
            break
    data = "\n".join(lines)
    return data


if __name__ == "__main__":
    change_sftp()
