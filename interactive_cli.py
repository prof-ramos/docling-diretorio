#!/usr/bin/env python3
"""CLI interativo para conversão de diretórios usando Docling.

Este script solicita interativamente o caminho do diretório,
processa os arquivos suportados e fornece feedback visual colorido.
"""

import subprocess
import sys
from pathlib import Path
from typing import List

try:
    from colorama import Fore, Style, init as colorama_init
except ImportError:
    class _DummyColor:
        BLACK = BLUE = CYAN = GREEN = MAGENTA = RED = WHITE = YELLOW = ""
        RESET_ALL = ""

    Fore = Style = _DummyColor()

    def colorama_init(*_args, **_kwargs) -> None:
        print("colorama não encontrado. Instale com 'pip install colorama' para saída colorida.")

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *_, **__):
        for item in iterable:
            yield item

    def _tqdm_write(message: str) -> None:
        print(message)

    tqdm.write = _tqdm_write
    print("tqdm não encontrado. Instale com 'pip install tqdm' para barra de progresso.")

# Extensões suportadas
SUPPORTED_SUFFIXES = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".csv", ".md", ".txt", ".html", ".htm", ".xml",
    ".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif",
    ".wav", ".mp3", ".aac", ".flac",
}


def solicitar_caminho_diretorio() -> Path:
    """Solicita o caminho do diretório via input()."""
    while True:
        caminho = input("Digite o caminho do diretório a ser processado: ").strip()
        if not caminho:
            print(f"{Fore.YELLOW}Um caminho é necessário.{Style.RESET_ALL}")
            continue

        caminho_path = Path(caminho).expanduser().resolve()
        if caminho_path.exists() and caminho_path.is_dir():
            return caminho_path
        else:
            print(f"{Fore.RED}O caminho '{caminho_path}' não existe ou não é um diretório.{Style.RESET_ALL}")


def listar_arquivos_suportados(diretorio: Path) -> List[Path]:
    """Lista todos os arquivos suportados no diretório."""
    arquivos = []
    for path in diretorio.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            arquivos.append(path)
    return arquivos


def executar_docling(arquivo: Path, diretorio_saida: Path) -> bool:
    """Executa o comando docling para um arquivo."""
    diretorio_saida.mkdir(parents=True, exist_ok=True)
    cmd = ["docling", "--output", str(diretorio_saida), str(arquivo)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            tqdm.write(f"{Fore.RED}Falha no processamento de {arquivo}: {result.stderr}{Style.RESET_ALL}")
            return False
        return True
    except FileNotFoundError:
        tqdm.write(f"{Fore.RED}CLI do Docling não encontrado. Instale o docling e tente novamente.{Style.RESET_ALL}")
        return False


def main():
    colorama_init(autoreset=True)

    print(f"{Fore.CYAN}CLI Interativo para Conversão de Diretórios{Style.RESET_ALL}")
    print("Este script processa arquivos suportados usando Docling.\n")

    try:
        diretorio_origem = solicitar_caminho_diretorio()
        print(f"{Fore.GREEN}Diretório selecionado: {diretorio_origem}{Style.RESET_ALL}")

        arquivos = listar_arquivos_suportados(diretorio_origem)
        if not arquivos:
            print(f"{Fore.YELLOW}Nenhum arquivo suportado encontrado no diretório.{Style.RESET_ALL}")
            return

        print(f"{Fore.BLUE}Encontrados {len(arquivos)} arquivo(s) para processar.{Style.RESET_ALL}")

        diretorio_saida = diretorio_origem / "output"
        diretorio_saida.mkdir(parents=True, exist_ok=True)

        falhas = []
        for arquivo in tqdm(arquivos, desc="Processando", unit="arquivo"):
            sucesso = executar_docling(arquivo, diretorio_saida)
            if not sucesso:
                falhas.append(arquivo)

        if falhas:
            print(f"{Fore.RED}Processamento concluído com {len(falhas)} falha(s).{Style.RESET_ALL}")
            for falha in falhas:
                print(f"  - {falha}")
        else:
            print(f"{Fore.GREEN}Processamento concluído com sucesso!{Style.RESET_ALL}")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operação cancelada pelo usuário.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Erro inesperado: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
