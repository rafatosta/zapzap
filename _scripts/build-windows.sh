#!/bin/bash

# Diretório contendo os arquivos .ui
UI_DIR="./zapzap/ui/"
# Diretório para saída dos arquivos .py gerados
OUTPUT_DIR="./zapzap/views/"

# Itera sobre todos os arquivos com extensão .ui no diretório especificado
for file in "${UI_DIR}"*.ui; do
  # Extrai o nome do arquivo sem a extensão .ui
  filename=$(basename "$file" .ui)

  # Define o caminho completo para o arquivo de saída com extensão .py
  OUTPUT_FILE="${OUTPUT_DIR}${filename}.py"

  # Exibe uma mensagem indicando qual arquivo está sendo gerado
  echo "Generating ${OUTPUT_FILE}"

  # Converte o arquivo .ui em um arquivo .py usando o comando do PyQt6
  python3 -m PyQt6.uic.pyuic -o "$OUTPUT_FILE" -x "$file"

  # Realiza modificações no arquivo gerado para suportar tradução com gettext
  sed -i 's/_translate = QtCore.QCoreApplication.translate//g' "$OUTPUT_FILE"
  sed -i 's/_translate(".*", /_(/g' "$OUTPUT_FILE"
  sed -i '1i\from gettext import gettext as _' "$OUTPUT_FILE"
done
