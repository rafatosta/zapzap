# Experimental performance settings

Experimental performance settings can change how QtWebEngine and Chromium use
the GPU, memory, and processes. Restart ZapZap after changing an option when the
restart prompt is shown.

## HTTP cache size

The cache size is expressed in MiB because Qt receives a byte count calculated
with 1024 × 1024. `0 MiB` lets Qt manage the limit automatically. The largest
selectable value is `2047 MiB`, which keeps the byte count within the signed
32-bit range accepted by `QWebEngineProfile`. Older or corrupted values outside
that range are repaired to automatic mode during loading; if Qt still rejects
the setting, ZapZap retries with automatic mode and continues startup.

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
