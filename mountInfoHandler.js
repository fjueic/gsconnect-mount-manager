const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;

function getDeviceIdList() {
    const command = "dconf list /org/gnome/shell/extensions/gsconnect/device/";
    const [res, out, err, status] = GLib.spawn_command_line_sync(command);
    let decoder = new TextDecoder();
    let result = decoder.decode(out).split("\n");
    for (let i = 0; i < result.length; i++) {
        if (result[i] == "") {
            result.splice(i, 1);
        }
    }
    return result; // [id1, id2, ...]
}

function getDeviceLastIpPort(id) {
    const command = `dconf read /org/gnome/shell/extensions/gsconnect/device/${id}last-connection`;
    const [res, out, err, status] = GLib.spawn_command_line_sync(command);
    let decoder = new TextDecoder();
    let result = decoder.decode(out).split("\n")[0].split("'")[1];
    result = result.slice("lan://".length).split(":");
    return result; // [ip, port]
}
function getDeviceName(id) {
    const command =
        "dconf read /org/gnome/shell/extensions/gsconnect/device/" +
        id +
        "name";
    const [res, out, err, status] = GLib.spawn_command_line_sync(command);
    let decoder = new TextDecoder();
    let result = decoder.decode(out).split("\n")[0].split("'")[1];
    return result; // name
}

function stringArrayToDconfString(stringArray) {
    // stringArray: ["a", "b", "c"] to "['a','b','c']"
    let result = '"[';
    for (let i = 0; i < stringArray.length; i++) {
        result += "'" + stringArray[i] + "',";
    }
    result = result.slice(0, -1);
    result += '"]';
    return result;
}
function fakeDconfChangeTigger(id) {
    // get the fake-change-trigger
    let command =
        "dconf read /org/gnome/shell/extensions/gsconnect/device/" +
        id +
        "fake-change-trigger";
    const [res, out, err, status] = GLib.spawn_command_line_sync(command);
    let decoder = new TextDecoder();
    let result = decoder.decode(out);
    if (result == "") {
        result = 0;
    } else {
        result = parseInt(result);
    }
    result++;
    result %= 10;
    // set the fake-change-trigger
    command =
        "dconf write /org/gnome/shell/extensions/gsconnect/device/" +
        id +
        "fake-change-trigger " +
        result;
    GLib.spawn_command_line_sync(command);
}
function createDummyFileStructure(name, id, multiPaths, pathNames) {
    id_ = id.split("/")[0];
    // check if .gsconnectMounts exists in home
    let command = `mkdir -p "${GLib.get_home_dir()}/.gsconnectMounts"`;
    GLib.spawn_command_line_sync(command);
    // create dummy file structure
    let name_ = `${name}___${id_}`;
    command = `rm -rf "${GLib.get_home_dir()}/.gsconnectMounts/${name_}/"`;
    GLib.spawn_command_line_sync(command);
    command = `mkdir -p "${GLib.get_home_dir()}/.gsconnectMounts/${name_}"`;
    GLib.spawn_command_line_sync(command);
    // create softlinks to dummy file structure
    for (let i = 0; i < multiPaths.length; i++) {
        command = `ln -s "${GLib.get_home_dir()}/.gsconnectMounts/${name_}" "${GLib.get_home_dir()}/.gsconnectMounts/${name_}/${
            pathNames[i]
        }"`;
        GLib.spawn_command_line_sync(command);
    }
}
function removeBookmark(id) {
    let file = Gio.File.new_for_path(
        GLib.get_home_dir() + "/.config/gtk-3.0/bookmarks"
    );
    let [ok, contents, etag] = file.load_contents(null);
    let decoder = new TextDecoder();
    let result = decoder.decode(contents);
    let name = getDeviceName(id);
    let line = `file://${GLib.get_home_dir()}/.gsconnectMounts/${name}___${id.split("/")[0]}`;
    line = line.replace(/ /g, "%20");
    line = line + " " + name;
    if (!result.includes(line)) {
        return;
    }
    result = result.replace(line + "\n", "");
    let encoder = new TextEncoder();
    let data = encoder.encode(result);
    file.replace_contents(
        data,
        null,
        false,
        Gio.FileCreateFlags.REPLACE_DESTINATION,
        null
    );
}
function addBookmark(id) {
    // /home/minoru/.config/gtk-3.0/bookmarks
    let file = Gio.File.new_for_path(
        GLib.get_home_dir() + "/.config/gtk-3.0/bookmarks"
    );
    let [ok, contents, etag] = file.load_contents(null);
    let decoder = new TextDecoder();
    let result = decoder.decode(contents);
    let name = getDeviceName(id);
    let line = `file://${GLib.get_home_dir()}/.gsconnectMounts/${name}___${id.split("/")[0]}`;
    line = line.replace(/ /g, "%20");
    line = line + " " + name;
    if (result.includes(line)) {
        return;
    }
    result += line + "\n";
    let encoder = new TextEncoder();
    let data = encoder.encode(result);
    file.replace_contents(
        data,
        null,
        false,
        Gio.FileCreateFlags.REPLACE_DESTINATION,
        null
    );
}
function addInfoDconf(data) {
    let mount_port = data.body.port;
    let ip = data.body.ip;
    let multiPaths = data.body.multiPaths;
    let pathNames = data.body.pathNames;
    let id = null;
    let deviceIdList = getDeviceIdList();
    for (let i = 0; i < deviceIdList.length; i++) {
        let [ip_, port_] = getDeviceLastIpPort(deviceIdList[i]);
        if (ip_ == ip) {
            id = deviceIdList[i];
            break;
        }
    }
    let name = getDeviceName(id);
    if (id == null) {
        return;
    }
    console.log(id, name, mount_port, multiPaths, pathNames);
    let command =
        "dconf write /org/gnome/shell/extensions/gsconnect/device/" +
        id +
        "mount-port " +
        mount_port;
    GLib.spawn_command_line_sync(command);
    command =
        "dconf write /org/gnome/shell/extensions/gsconnect/device/" +
        id +
        "multi-paths " +
        stringArrayToDconfString(multiPaths);
    GLib.spawn_command_line_sync(command);
    command =
        "dconf write /org/gnome/shell/extensions/gsconnect/device/" +
        id +
        "path-names " +
        stringArrayToDconfString(pathNames);
    GLib.spawn_command_line_sync(command);
    createDummyFileStructure(name, id, multiPaths, pathNames);
    addBookmark(id);
}
