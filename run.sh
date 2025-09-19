#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verificar se uv está instalado
if ! command -v uv &> /dev/null; then
    echo "uv não encontrado. Instalando uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Criar ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    uv venv
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar e instalar dependências
echo "Verificando dependências..."
uv pip install --quiet colorama tqdm docling

# Executar o script interativo
exec python3 "${SCRIPT_DIR}/interactive_cli.py"
