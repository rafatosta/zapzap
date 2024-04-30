# Flatpak Development

### Local dependencies
- python >= 3.9
- flatpak-builder

### Download the application
```bash
git clone https://github.com/zapzap-linux/zapzap.git
cd zapzap
```

### Installing dependencies
```bash
# add flathub remote
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# installing required packages
flatpak install --user --assumeyes flathub org.kde.Platform//6.6 com.riverbankcomputing.PyQt.BaseApp//6.6
```

## Building Single-file

Generates a unique file for installation and distribution
```bash
# Building and Running
python _packaging/flatpak/build_single_file.py
```

At the end, the file for installation will be in the 'export' folder with the name zapzap.flatpak.
For installation:
```bash
flatpak install export/zapzap.flatpak
```
