Compile Deb package:

    Create release file.

    dch --create -D stable --package "immutable-deepin-tools" --newversion=1.x.x "New release."

    Compilation Dependencies:

    sudo apt build-dep .

    Compile Package:

    dpkg-buildpackage -Zxz -rfakeroot -b
