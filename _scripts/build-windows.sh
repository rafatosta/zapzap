#!/bin/bash

UI_DIR="./zapzap/ui/"
OUTPUT_DIR="./zapzap/views/"
APP_ID="com.rtosta.zapzap"

generate_with_local() {
  python3 -m PyQt6.uic.pyuic "$@"
}

generate_with_flatpak() {
  flatpak run --filesystem=$(pwd) --command=python3 "$APP_ID" \
    -m PyQt6.uic.pyuic "$@"
}

# Detecta se PyQt6 está disponível no host
if python3 -c "import PyQt6" &> /dev/null; then
  echo "✔ Using local PyQt6"
  GENERATOR=generate_with_local
else
  echo "⚠ PyQt6 not found locally, using Flatpak"
  GENERATOR=generate_with_flatpak
fi

for file in "${UI_DIR}"*.ui; do
  filename=$(basename "$file" .ui)
  OUTPUT_FILE="${OUTPUT_DIR}${filename}.py"

  echo "Generating ${OUTPUT_FILE}"

  $GENERATOR -o "$OUTPUT_FILE" -x "$file"

  sed -i 's/_translate = QtCore.QCoreApplication.translate//g' "$OUTPUT_FILE"
  sed -i 's/_translate(".*", /_(/g' "$OUTPUT_FILE"
  sed -i '1i\from gettext import gettext as _' "$OUTPUT_FILE"
done