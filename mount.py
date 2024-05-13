
import os
import subprocess
import json

def getDeviceIdList():
    command = "dconf list /org/gnome/shell/extensions/gsconnect/device/"
    res = subprocess.run(command, shell=True, capture_output=True)
    result = res.stdout.decode().split("\n")
    result = list(filter(None, result))
    return result

def getDeviceLastIpPort(id):
    command = f"dconf read /org/gnome/shell/extensions/gsconnect/device/{id}last-connection"
    res = subprocess.run(command, shell=True, capture_output=True)
    result = res.stdout.decode().split("\n")[0].split("'")[1]
    result = result[len("lan://"):].split(":")
    return result

def getDeviceName(id):
    command = f"dconf read /org/gnome/shell/extensions/gsconnect/device/{id}name"
    res = subprocess.run(command, shell=True, capture_output=True)
    result = res.stdout.decode().split("\n")[0].split("'")[1]
    return result

def stringArrayToDconfString(stringArray):
    result = '"['
    for i in range(len(stringArray)):
        result += "'" + stringArray[i] + "',"
    result = result[:-1]
    result += ']"'
    return result

def createDummyFileStructure(name, id, multiPaths, pathNames):
    id_ = id.split("/")[0]
    command = f"mkdir -p \"{os.path.expanduser('~')}/.gsconnectMounts\""
    os.system(command)
    name_ = f"{name}___{id_}"
    command = f"rm -rf \"{os.path.expanduser('~')}/.gsconnectMounts/{name_}/\""
    os.system(command)
    command = f"mkdir -p \"{os.path.expanduser('~')}/.gsconnectMounts/{name_}\""
    os.system(command)
    for i in range(len(multiPaths)):
        command = f"ln -s \"{os.path.expanduser('~')}/.gsconnectMounts/{name_}\" \"{os.path.expanduser('~')}/.gsconnectMounts/{name_}/{pathNames[i]}\""
        os.system(command)

def removeBookmark(id):
    file = os.path.expanduser('~') + "/.config/gtk-3.0/bookmarks"
    with open(file, 'r') as f:
        result = f.read()
    name = getDeviceName(id)
    line = f"file://{os.path.expanduser('~')}/.gsconnectMounts/{name}___{id.split('/')[0]}"
    line = line.replace(" ", "%20")
    line = line + " " + name
    if line not in result:
        return
    result = result.replace(line + "\n", "")
    with open(file, 'w') as f:
        f.write(result)

def addBookmark(id):
    file = os.path.expanduser('~') + "/.config/gtk-3.0/bookmarks"
    with open(file, 'r') as f:
        result = f.read()
    name = getDeviceName(id)
    line = f"file://{os.path.expanduser('~')}/.gsconnectMounts/{name}___{id.split('/')[0]}"
    line = line.replace(" ", "%20")
    line = line + " " + name
    if line in result:
        return
    result += line + "\n"
    with open(file, 'w') as f:
        f.write(result)

def addInfoDconf():
    path = os.path.expanduser('~') + "/.config/gsconnect-mount-manager/temp.json"
    with open(path, 'r') as f:
        data = json.load(f)
    mount_port = data['body']['port']
    ip = data['body']['ip']
    multiPaths = data['body']['multiPaths']
    pathNames = data['body']['pathNames']
    id = None
    deviceIdList = getDeviceIdList()
    for i in range(len(deviceIdList)):
        ip_, port_ = getDeviceLastIpPort(deviceIdList[i])
        if ip_ == ip:
            id = deviceIdList[i]
            break
    name = getDeviceName(id)
    if id == None:
        return
    command = f"dconf write /org/gnome/shell/extensions/gsconnect/device/{id}mount-port {mount_port}"
    os.system(command)
    command = f"dconf write /org/gnome/shell/extensions/gsconnect/device/{id}multi-paths {stringArrayToDconfString(multiPaths)}"
    os.system(command)
    command = f"dconf write /org/gnome/shell/extensions/gsconnect/device/{id}path-names {stringArrayToDconfString(pathNames)}"
    os.system(command)
    createDummyFileStructure(name, id, multiPaths, pathNames)
    addBookmark(id)
    with open(path, 'w') as f:
        f.write("")

def main():
    import sys
    args = sys.argv[1]
    if args == "add":
        addInfoDconf()
    elif args == "remove":
        id = sys.argv[2]
        removeBookmark(id)

if __name__ == "__main__":
    main()
