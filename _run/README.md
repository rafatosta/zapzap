# Local Development

### Mandatory dependencies
- python >= 3.9
- flatpak-builder

### Download the application
```bash
git clone https://github.com/zapzap-linux/zapzap.git
cd zapzap
```

## Local run
#### Installing dependencies
```bash
pip install PyQt6 PyQt6-WebEngine dbus-python python-gettext
```
#### Run
```bash
python _run/run.py
```

## Flatpak run

### Installing dependencies
```bash
# add flathub remote
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# installing required packages
flatpak install --user --assumeyes flathub org.kde.Platform//6.6 org.kde.Sdk//6.6 com.riverbankcomputing.PyQt.BaseApp//6.6 
```
## Running the application

```bash
# Building and Running
python _run/run_flatpak.py
```
