# Experimental performance settings

Experimental performance settings can change how QtWebEngine and Chromium use
the GPU, memory, and processes. Restart ZapZap after changing an option when the
restart prompt is shown.

## Rendering profiles

The rendering profile is a convenience layer over the existing GPU and
rendering switches. All advanced controls remain visible and editable. The
effective values are the source of truth: ZapZap reports **Default** or
**Compatibility** only when every controlled setting matches that preset, and
reports **Manual** otherwise. This preserves settings created by older versions
without a migration or a separate mode marker. Editing a controlled switch
immediately recalculates the profile; recreating an exact preset selects it
again automatically.

Both presets keep the automatic multi-GPU workaround enabled and leave cache,
process, JavaScript memory, background, accessibility, zoom, proxy, Wayland and
account preferences unchanged. Their exact controlled values are:

| Setting | Default | Compatibility |
|---|---:|---:|
| In-process GPU | off | off |
| Disable GPU | off | off |
| Automatic multi-GPU workaround | on | on |
| Disable GPU VSync | off | off |
| Force software rendering | off | off |
| Disable GPU memory buffer for video | off | on |
| Disable zero-copy | off | on |
| Use software video decoding | off | on |
| Force GBM | off | off |

Compatibility therefore adds
`--disable-gpu-memory-buffer-video-frames`, `--disable-zero-copy`, and
`--disable-accelerated-video-decode` at the next application start. It does not
add `--disable-gpu`, set `QT_OPENGL=software`, or change the Chromium process
model. Existing unrelated Chromium flags and ZapZap's mandatory flags remain
in place.

## HTTP cache size

The cache size is expressed in MiB because Qt receives a byte count calculated
with 1024 × 1024. `0 MiB` lets Qt manage the limit automatically. The largest
selectable value is `2047 MiB`, which keeps the byte count within the signed
32-bit range accepted by `QWebEngineProfile`. Older or corrupted values outside
that range are repaired to automatic mode during loading; if Qt still rejects
the setting, ZapZap retries with automatic mode and continues startup.
Unsupported cache-type values are repaired to disk cache. If Qt rejects the
selected type, ZapZap also retries with disk cache without stopping the account.

## Persistent cookies and JavaScript memory

**Persistent cookies** now maps directly to the persistent-cookie policy of
every account profile. If Qt rejects that policy, ZapZap preserves Qt's
persistent default so profile creation can continue.

The JavaScript memory selector stores its current stable index and synchronizes
the legacy MiB key for compatibility. At the next full restart, the selected
numeric value becomes Chromium's `--max-old-space-size` setting; **Automatic**
does not add a memory-limit flag.

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
