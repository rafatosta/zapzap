$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt
python -m builders.windows.windows_builder
Get-ChildItem -Path dist
