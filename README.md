# Conversor de Diretórios Docling

Este projeto fornece ferramentas para conversão em lote de documentos usando o Docling. Permite processar diretórios inteiros de forma recursiva, convertendo arquivos suportados para formatos estruturados.

## Funcionalidades

- **Conversão em lote**: Processa diretórios inteiros recursivamente
- **Interface CLI**: Comando direto via linha de comando
- **Interface interativa**: CLI guiada para seleção de diretórios
- **Suporte a múltiplos formatos**: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, CSV, MD, TXT, HTML, XML, imagens e áudio
- **Relatório de falhas**: Gera relatório de arquivos que falharam na conversão
- **Barra de progresso**: Visualização do progresso com tqdm (opcional)
- **Saída colorida**: Mensagens coloridas com colorama (opcional)

## Instalação

### Opção 1: Usando uv (Recomendado)

```bash
./run.sh
```

Este comando instala automaticamente o uv, cria um ambiente virtual e instala todas as dependências.

### Opção 2: Usando pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install docling tqdm colorama
```

## Uso

### Interface Interativa (Recomendado para iniciantes)

```bash
python interactive_cli.py
# ou
./run.sh
```

A interface interativa irá solicitar o caminho do diretório e processar todos os arquivos suportados.

### Comando Direto

```bash
python convert_directory.py /caminho/para/diretorio --output saida --verbose
```

#### Opções disponíveis:

- `source`: Arquivo ou diretório para processar (obrigatório)
- `--output`: Diretório de saída (padrão: `docling-output`)
- `--to`: Formato de saída do Docling (ex: md, json)
- `--skip-existing`: Pula arquivos já processados
- `--verbose`: Mostra saída detalhada do Docling

## Formatos Suportados

- **Documentos**: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX
- **Texto**: CSV, MD, TXT, HTML, HTM, XML
- **Imagens**: JPG, JPEG, PNG, TIFF, BMP, GIF
- **Áudio**: WAV, MP3, AAC, FLAC

## Estrutura de Saída

O conversor mantém a estrutura de diretórios do fonte, organizando os artefatos do Docling por pasta de origem.

```
diretorio_origem/
├── pasta1/
│   ├── documento.pdf
│   └── documento.docx
└── pasta2/
    └── imagem.jpg

# Gera:
diretorio_saida/
├── pasta1/
│   ├── documento/  # Artefatos do PDF
│   └── documento/  # Artefatos do DOCX
└── pasta2/
    └── imagem/     # Artefatos da imagem
```

## Tratamento de Erros

- Arquivos que falham na conversão são listados em `failed_conversions.txt`
- O programa continua processando outros arquivos mesmo se alguns falharem
- Mensagens de erro são exibidas em vermelho com contexto detalhado

## Dependências

### Obrigatórias:
- **docling**: CLI principal para conversão de documentos
- **Python 3.10+**: Versão mínima necessária

### Opcionais:
- **tqdm**: Barra de progresso visual
- **colorama**: Saída colorida no terminal
- **tkinter**: Interface gráfica para seleção de diretórios (Linux/Mac)

## Desenvolvimento

### Configuração do ambiente de desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install ruff flake8

# Verificar código
ruff check .

# Formatar código
ruff format .
```

### Estrutura do projeto

- `convert_directory.py`: Script principal de conversão
- `interactive_cli.py`: Interface interativa
- `run.sh`: Script de inicialização automatizada
- `AGENTS.md`: Diretrizes para agentes de codificação

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.

## Suporte

Para problemas ou sugestões, abra uma issue no repositório do projeto.</content>
</xai:function_call">README.md