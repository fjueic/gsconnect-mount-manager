# enabling service
systemctl --user daemon-reload
systemctl --user enable gsconnect-mount-manager.service
systemctl --user start gsconnect-mount-manager.service