#!/bin/bash

set -e

echo "🔍 Verificando se o Docker está instalado..."
if ! command -v docker &> /dev/null; then
  echo "❌ Docker não está instalado."
  exit 1
fi

echo "✅ Docker instalado."

echo "🔄 Verificando se o serviço Docker está rodando..."
if ! systemctl is-active --quiet docker; then
  echo "⚙️ Iniciando o serviço Docker..."
  sudo systemctl start docker
else
  echo "✅ Docker já está em execução."
fi

echo "🐳 Iniciando build com electronuserland/builder..."

docker run --rm -ti \
  -v "$PWD":/project \
  -w /project \
  electronuserland/builder \
  bash -c "yarn install && yarn run electron-builder --linux rpm"

echo "✅ Build finalizado!"