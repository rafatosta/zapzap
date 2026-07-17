from zapzap.core.diagnostics.crash_dump_handler import CrashDumpHandler
from zapzap import __appname__

crash_handler = CrashDumpHandler(
    app_name=__appname__,
    show_dialog=True
)
