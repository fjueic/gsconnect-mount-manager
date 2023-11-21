import sys
import os
args = sys.argv
home = args[1]
def change_sftp():
    # ~/.local/share/gnome-shell/extensions/gsconnect@andyholmes.github.io/service/plugins/sftp.js
    with open(f"{os.path.join(home, '.local/share/gnome-shell/extensions/gsconnect@andyholmes.github.io/service/plugins/sftp.js')}", 'r+') as f:
        data = f.read()
        data = addImports(data)
        data = addMountingLogic(data)
        data = addunMountingLogic(data)
        f.seek(0)
        f.write(data)
    

def addImports(data):
    lines = data.split('\n')
    for i in range(len(lines)):
        if "backends.lan" in lines[i]:
            lines[i] = lines[i] + """
// this block of code is not part of gsconnect connect extension
const MountHandler = imports.service.utils.mountInfoHandler;
// end of block"""
            break
    data = '\n'.join(lines)
    return data

def addMountingLogic(data):
    lines = data.split('\n')
    for i in range(len(lines)):
        if "else" in lines[i] and "this._handleMount(packet)" in lines[i+1]:
            lines[i] = """              else{ // if script is editing the file, don't forget to place {} around else
                    // this block of code is not part of gsconnect connect extension
                    try{
                        MountHandler.addInfoDconf(packet);
                    }catch(e){
                        pass
                    }
                    // end of block
                    this._handleMount(packet);
                }"""
            lines[i+1] = ""
            break
    data = '\n'.join(lines)
    return data

def addunMountingLogic(data):
    lines = data.split('\n')
    for i in range(len(lines)):
        if "_onMountRemoved(monitor" in lines[i]:
            lines[i] =lines[i] + """
        // this block of code is not part of gsconnect connect extension
        try{
            MountHandler.removeBookmark(this._device._id + "/");
        }catch(e){
            pass
        }
        // end of block"""
            break
    data = '\n'.join(lines)
    return data

if __name__ == "__main__":
    change_sftp()