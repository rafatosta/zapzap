#!/bin/bash

# Itera sobre todos os arquivos com extensão .ui no diretório ./zapzap/ui/
for file in ./zapzap/ui/*.ui; do
  # Extrai apenas o nome do arquivo sem a extensão .ui
  filename=$(basename "$file" .ui)

  # Define o caminho completo para o arquivo de saída com extensão .py
  OUTPUT_FILE="./zapzap/views/${filename}.py"

  # Exibe uma mensagem indicando qual arquivo está sendo gerado
  echo "Generating ${OUTPUT_FILE}"

  # Executa o comando para converter o arquivo .ui em um arquivo .py
  python3 -m PyQt6.uic.pyuic -o "$OUTPUT_FILE" -x "$file"
done
