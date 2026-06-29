from pathlib import Path
import subprocess
import sys
import re


class UiCompiler:
    def __init__(
        self,
        ui_dir: str = "./zapzap/ui/",
        output_dir: str = "./zapzap/views/",
        app_id: str = "com.rtosta.zapzap",
    ):
        self.ui_dir = Path(ui_dir)
        self.output_dir = Path(output_dir)
        self.app_id = app_id

        self.generator = (
            self.generate_with_local
            if self.has_local_pyqt6()
            else self.generate_with_flatpak
        )

    def has_local_pyqt6(self) -> bool:
        """Verifica se o PyQt6 está disponível localmente."""

        try:
            subprocess.run(
                [sys.executable, "-c", "import PyQt6"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            print("✔ Using local PyQt6")

            return True

        except subprocess.CalledProcessError:
            print("⚠ PyQt6 not found locally, using Flatpak")

            return False

    def generate_with_local(
        self,
        output_file: Path,
        ui_file: Path,
    ):
        """Gera arquivo Python usando PyQt6 local."""

        subprocess.run(
            [
                sys.executable,
                "-m",
                "PyQt6.uic.pyuic",
                "-o",
                str(output_file),
                "-x",
                str(ui_file),
            ],
            check=True,
        )

    def generate_with_flatpak(
        self,
        output_file: Path,
        ui_file: Path,
    ):
        """Gera arquivo Python usando Flatpak."""

        subprocess.run(
            [
                "flatpak",
                "run",
                f"--filesystem={Path.cwd()}",
                "--command=python3",
                self.app_id,
                "-m",
                "PyQt6.uic.pyuic",
                "-o",
                str(output_file),
                "-x",
                str(ui_file),
            ],
            check=True,
        )

    def remove_pyuic_header(self, content: str) -> str:
        """Remove cabeçalho variável gerado pelo pyuic."""

        lines = content.splitlines()

        filtered_lines = []
        skipping = False

        for line in lines:
            if line.startswith(
                "# Form implementation generated from reading ui file"
            ):
                skipping = True
                continue

            if skipping:
                if line.strip() == "":
                    skipping = False

                continue

            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def apply_translations(self, content: str) -> str:
        """Converte _translate para gettext."""

        content = content.replace(
            "_translate = QtCore.QCoreApplication.translate",
            "",
        )

        content = re.sub(
            r'_translate\(".*?", ',
            "_(",
            content,
        )

        return content

    def ensure_gettext_import(self, content: str) -> str:
        """Adiciona import do gettext."""

        import_line = "from gettext import gettext as _"

        if import_line not in content:
            content = f"{import_line}\n{content}"

        return content

    def normalize_content(self, content: str) -> str:
        """Aplica normalizações no conteúdo gerado."""

        content = self.remove_pyuic_header(content)

        content = self.apply_translations(content)

        content = self.ensure_gettext_import(content)

        return content.strip() + "\n"

    def post_process(self, output_file: Path):
        """Aplica pós-processamento no arquivo gerado."""

        content = output_file.read_text(encoding="utf-8")

        content = self.normalize_content(content)

        old_content = ""

        if output_file.exists():
            old_content = output_file.read_text(encoding="utf-8")

        if old_content != content:
            output_file.write_text(content, encoding="utf-8")

            print(f"✔ Updated {output_file}")

        else:
            print(f"➜ No changes in {output_file}")

    def compile_ui_file(self, ui_file: Path):
        """Compila um único arquivo .ui."""

        output_file = self.output_dir / f"{ui_file.stem}.py"

        print(f"Generating {output_file}")

        self.generator(output_file, ui_file)

        self.post_process(output_file)

    def compile_all(self):
        """Compila todos os arquivos .ui."""

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        ui_files = sorted(self.ui_dir.glob("*.ui"))

        if not ui_files:
            print("⚠ No .ui files found")

            return

        for ui_file in ui_files:
            self.compile_ui_file(ui_file)