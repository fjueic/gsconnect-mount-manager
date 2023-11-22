# check if root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)

block_of_code="this block of code is not part of gsconnect connect extension"
if grep -q "$block_of_code" "$USER_HOME/.local/share/gnome-shell/extensions/gsconnect@andyholmes.github.io/service/plugins/sftp.js"; then
  echo "Reinstall gsconnect extension and try again"
  exit 1
fi

# changing directory to the script directory
script_dir=$(dirname "$0")
cd "$script_dir" || exit # Exit the script if cd doesn't work, prevents next commands from running

# putting files in place
cp -f ./mountInfoHandler.js "$USER_HOME/.local/share/gnome-shell/extensions/gsconnect@andyholmes.github.io/service/utils/"
mkdir -p "$USER_HOME/.config/gsconnect-mount-manager/" && cp -f ./run.py "$USER_HOME/.config/gsconnect-mount-manager/"
[ -e /etc/systemd/user/gsconnect-mount-manager.service ] || touch /etc/systemd/user/gsconnect-mount-manager.service

# update service file
chmod +x ./update_servicefile.py
python3 ./update_servicefile.py "$USER_HOME" "$script_dir" >/etc/systemd/user/gsconnect-mount-manager.service

# editing sftp.js in gsconnect extension
chmod +x ./update_sftp.py
python3 ./update_sftp.py "$USER_HOME"

echo "Done!"
