# Experimental performance settings

Experimental performance settings can change how QtWebEngine and Chromium use
the GPU, memory, and processes. Restart ZapZap after changing an option when the
restart prompt is shown.

## Software video decoding

Enable **Use software video decoding** when:

- a video plays audio but does not show an image;
- the video area appears white or black;
- the interface flickers when a video opens;
- GIFs or status media are not rendered;
- ZapZap closes while playing media.

This option adds `--disable-accelerated-video-decode` to QtWebEngine's Chromium
flags at the next application start, regardless of whether ZapZap is installed
through Flatpak, DEB, RPM, AppImage, Snap, or run from source. It does not
disable all GPU acceleration. Software decoding can increase CPU usage and
battery consumption, so leave the option disabled unless it is needed as a
compatibility workaround.
