import os

os.system('./scripts/build-windows.sh')

os.system('./scripts/build-translations.sh')

os.system('python -m zapzap ')