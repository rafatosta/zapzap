#!/bin/bash

# Caminho para o arquivo que lista os diretórios a serem analisados
DIRECTORIES_FILE="./po/POTFILES"

# Caminho para o arquivo template de mensagens (POT)
POT_FILE="./po/zapzap.pot"

# Diretório base para os arquivos .po
PO_DIR="./po"

# Diretório base para os arquivos .mo
MO_BASE_DIR="./zapzap/po"

# Encontrar todos os arquivos nos diretórios especificados no DIRECTORIES_FILE
SOURCE_FILES=$(find $(cat "$DIRECTORIES_FILE") -type f -name "*.py")

# Geração do arquivo template POT com base nos arquivos encontrados
xgettext --from-code=UTF-8 --keyword=_ --output="$POT_FILE" $SOURCE_FILES

# Ajustar a codificação do arquivo POT para UTF-8
sed -i 's/charset=CHARSET/charset=UTF-8/g' "$POT_FILE"

# Loop pelas linhas no arquivo LINGUAS para processar cada idioma listado
LINGUAS_FILE="./po/LINGUAS"
while IFS= read -r line || [[ -n "$line" ]]; do
  # Ignorar linhas vazias ou com espaços em branco
  if [[ -z "$line" || "$line" =~ ^[[:space:]]*$ ]]; then
    continue
  fi

  # Diretório para os arquivos .mo do idioma atual
  MO_DIR="${MO_BASE_DIR}/${line}/LC_MESSAGES/"
  mkdir -p "$MO_DIR"

  # Caminho do arquivo .po para o idioma atual
  PO_FILE="${PO_DIR}/${line}.po"

  # Verificar se o arquivo .po já existe
  if [ -f "$PO_FILE" ]; then
    echo "Ignorando ${line} (arquivo .po já existe)"
    # Atualizar o arquivo PO existente com as novas mensagens
    msgmerge -o "$PO_FILE" "$PO_FILE" "$POT_FILE"
  else
    echo "Gerando ${line} (novo arquivo .po)"
    # Criar um novo arquivo .po
    xgettext --from-code=UTF-8 --keyword=_ --output="$PO_FILE" $SOURCE_FILES
    # Ajustar a codificação do arquivo .po para UTF-8
    sed -i 's/charset=CHARSET/charset=UTF-8/g' "$PO_FILE"
    # Configurar o campo de idioma no arquivo .po
    sed -i 's/Language:/Language:'${line}'/g' "$PO_FILE"
  fi

  # Gerar o arquivo .mo correspondente
  msgfmt "$PO_FILE" -o "${MO_DIR}zapzap.mo"

  # Aviso sobre a geração do arquivo .mo
  if [ $? -eq 0 ]; then
    echo "Arquivo .mo gerado com sucesso para o idioma: ${line}"
  else
    echo "Erro ao gerar o arquivo .mo para o idioma: ${line}"
  fi

done < "$LINGUAS_FILE"
