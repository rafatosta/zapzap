from pathlib import Path
import subprocess
import re


class TranslationManager:
    IGNORE_PATTERNS = [
        r'"POT-Creation-Date: .*\\n"\n?',
        r'"PO-Revision-Date: .*\\n"\n?',
    ]

    def __init__(
        self,
        directories_file: str = "./po/POTFILES",
        linguas_file: str = "./po/LINGUAS",
        pot_file: str = "./po/zapzap.pot",
        po_dir: str = "./po",
        mo_base_dir: str = "./zapzap/po",
    ):
        self.directories_file = Path(directories_file)
        self.linguas_file = Path(linguas_file)
        self.pot_file = Path(pot_file)
        self.po_dir = Path(po_dir)
        self.mo_base_dir = Path(mo_base_dir)

    def run(self):
        source_files = self.get_source_files()

        if not source_files:
            print("Nenhum arquivo fonte encontrado.")
            return

        self.generate_pot(source_files)

        for language in self.get_languages():
            self.process_language(language, source_files)

    def get_source_files(self) -> list[str]:
        source_files = []

        if not self.directories_file.exists():
            print(f"Arquivo não encontrado: {self.directories_file}")
            return source_files

        directories = [
            line.strip()
            for line in self.directories_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        for directory in directories:
            path = Path(directory)

            if not path.exists():
                continue

            source_files.extend(
                str(file)
                for file in path.rglob("*.py")
            )

        return source_files

    def generate_pot(self, source_files: list[str]):
        print("Gerando arquivo POT...")

        old_raw_content = ""

        if self.pot_file.exists():
            old_raw_content = self.pot_file.read_text(
                encoding="utf-8"
            )

        command = [
            "xgettext",
            "--from-code=UTF-8",
            "--keyword=_",
            f"--output={self.pot_file}",
            *source_files,
        ]

        success = self.execute(command)

        if not success:
            return

        self.replace_charset(self.pot_file)

        new_raw_content = self.pot_file.read_text(
            encoding="utf-8"
        )

        old_normalized = self.normalize_content(
            old_raw_content
        )

        new_normalized = self.normalize_content(
            new_raw_content
        )

        if old_normalized == new_normalized:
            print("Nenhuma alteração real no arquivo POT.")

            self.pot_file.write_text(
                old_raw_content,
                encoding="utf-8",
            )

    def get_languages(self) -> list[str]:
        if not self.linguas_file.exists():
            print(f"Arquivo não encontrado: {self.linguas_file}")
            return []

        return [
            line.strip()
            for line in self.linguas_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def process_language(self, language: str, source_files: list[str]):
        mo_dir = self.mo_base_dir / language / "LC_MESSAGES"

        mo_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        po_file = self.po_dir / f"{language}.po"

        if po_file.exists():
            print(f"Ignorando {language} (arquivo .po já existe)")
            self.update_po(po_file)

        else:
            print(f"Gerando {language} (novo arquivo .po)")

            self.create_po(
                po_file,
                language,
                source_files,
            )

        self.generate_mo(
            po_file,
            mo_dir,
            language,
        )

    def update_po(self, po_file: Path):
        old_raw_content = po_file.read_text(
            encoding="utf-8"
        )

        command = [
            "msgmerge",
            "-o",
            str(po_file),
            str(po_file),
            str(self.pot_file),
        ]

        success = self.execute(command)

        if not success:
            return

        new_raw_content = po_file.read_text(
            encoding="utf-8"
        )

        old_normalized = self.normalize_content(
            old_raw_content
        )

        new_normalized = self.normalize_content(
            new_raw_content
        )

        if old_normalized == new_normalized:
            print(
                f"Nenhuma alteração real em {po_file.name}"
            )

            po_file.write_text(
                old_raw_content,
                encoding="utf-8",
            )

    def create_po(
        self,
        po_file: Path,
        language: str,
        source_files: list[str],
    ):
        command = [
            "xgettext",
            "--from-code=UTF-8",
            "--keyword=_",
            f"--output={po_file}",
            *source_files,
        ]

        success = self.execute(command)

        if not success:
            return

        self.replace_charset(po_file)

        self.set_language(
            po_file,
            language,
        )

    def generate_mo(
        self,
        po_file: Path,
        mo_dir: Path,
        language: str,
    ):
        mo_file = mo_dir / "zapzap.mo"

        command = [
            "msgfmt",
            str(po_file),
            "-o",
            str(mo_file),
        ]

        success = self.execute(command)

        if success:
            print(
                f"Arquivo .mo gerado com sucesso para o idioma: {language}"
            )

        else:
            print(
                f"Erro ao gerar o arquivo .mo para o idioma: {language}"
            )

    @staticmethod
    def replace_charset(file_path: Path):
        content = file_path.read_text(
            encoding="utf-8"
        )

        content = content.replace(
            "charset=CHARSET",
            "charset=UTF-8",
        )

        file_path.write_text(
            content,
            encoding="utf-8",
        )

    @staticmethod
    def set_language(
        file_path: Path,
        language: str,
    ):
        content = file_path.read_text(
            encoding="utf-8"
        )

        content = content.replace(
            "Language:",
            f"Language:{language}",
        )

        file_path.write_text(
            content,
            encoding="utf-8",
        )

    @classmethod
    def normalize_content(
        cls,
        content: str,
    ) -> str:
        normalized = content

        for pattern in cls.IGNORE_PATTERNS:
            normalized = re.sub(
                pattern,
                "",
                normalized,
                flags=re.MULTILINE,
            )

        return normalized.strip()

    @staticmethod
    def execute(command: list[str]) -> bool:
        try:
            subprocess.run(
                command,
                check=True,
            )

            return True

        except subprocess.CalledProcessError as error:
            print(
                f"Erro ao executar comando: {' '.join(command)}"
            )

            print(error)

            return False


if __name__ == "__main__":
    manager = TranslationManager()
    manager.run()