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

# Verificar e instalar dependências (incluindo Streamlit)
echo "Verificando dependências..."
uv pip install --quiet colorama tqdm docling streamlit streamlit-extras

# Verificar se streamlit está disponível
if ! command -v streamlit &> /dev/null; then
    echo "Erro: Streamlit não pôde ser instalado."
    exit 1
fi

# Executar a interface Streamlit
echo "Iniciando interface web..."
exec streamlit run "${SCRIPT_DIR}/app.py"