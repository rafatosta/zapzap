import os

# Build the windows from the .ui file
#os.system('./_scripts/build-windows.sh')

# Build the translations
os.system('./_scripts/build-translations.sh')

# Activate Custom Debug Settings
# debug = False

# Run the app
# os.system('python -m zapzap ' + ('--zapDebug' if debug ==
#          True else ''))
""" import os


def get_linux_distro():
    distro_name = "Desconhecida"
    distro_id = "0"
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                #print(line)
                if line.startswith("PRETTY_NAME"):
                    # Extrair o nome da distribuição
                    distro_name = line.split("=")[1].strip().replace('"', '')
                    #break
                if line.startswith("ID"):
                    # Extrair o ID da distribuição
                    distro_id = line.split("=")[1].strip().replace('"', '')
                    #break
    return distro_name, distro_id


print(f"\nDistro: {get_linux_distro()}\n") """
