from zapzap.core.diagnostics.crash_dump_handler import CrashDumpHandler
from zapzap.core.diagnostics.page_console_log import PageConsoleLog
from zapzap import __appname__

crash_handler = CrashDumpHandler(
    app_name=__appname__,
    show_dialog=True
)

# Compartilha o diretório do crash handler para que a página de Depuração
# exponha um único lugar com todos os arquivos de diagnóstico.
page_console_log = PageConsoleLog(crash_handler.dump_dir)
