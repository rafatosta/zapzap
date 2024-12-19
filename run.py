import os

def dev():
    """Run the app in development mode."""
    print("Starting app in development mode...")
    os.system("python -m zapzap")

def preview():
    """Run the app in preview mode."""
    print("Starting app in preview mode...")
    """ os.system("python zapzap/main.py --env=preview")
 """
def build():
    """Build the app for production."""
    print("Building the app for production...")
    """ os.makedirs("dist", exist_ok=True)
    os.system("pyinstaller --onefile zapzap/main.py -n zapzap")
    print("Build completed. Check the 'dist' folder.") """

if __name__ == "__main__":
    import sys

    commands = {
        "dev": dev,
        "preview": preview,
        "build": build,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(f"Usage: python run.py [dev|preview|build]")
    else:
        commands[sys.argv[1]]()
