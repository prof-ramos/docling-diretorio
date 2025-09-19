#!/usr/bin/env python3
"""Auxiliar de conversão em lote para Docling.

Este script percorre um diretório (recursivamente) e invoca o CLI `docling`
globalmente instalado para cada arquivo suportado encontrado. O objetivo é
facilitar o processamento de uma base de conhecimento ou árvore de documentos
no Docling sem precisar iterar manualmente sobre os arquivos.

Exemplo de uso:
    python convert_directory.py /caminho/para/fonte --output /caminho/para/saida

Por padrão, o script espelha a estrutura de diretórios sob a raiz de saída
escolhida para que os artefatos do Docling permaneçam agrupados por pasta
de origem.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

try:
    from colorama import Fore, Style, init as colorama_init
except ImportError:  # pragma: no cover - fallback for environments without colorama
    class _DummyColor:
        BLACK = BLUE = CYAN = GREEN = MAGENTA = RED = WHITE = YELLOW = ""
        RESET_ALL = ""

    Fore = Style = _DummyColor()  # type: ignore

    def colorama_init(*_args, **_kwargs) -> None:  # type: ignore
        print("Colorama não encontrado. Instale com 'pip install colorama' para saída colorida.")

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover - fallback for environments without tqdm
    def tqdm(iterable, *_, **__):  # type: ignore
        for item in iterable:
            yield item

    def _tqdm_write(message: str) -> None:
        print(message)

    tqdm.write = _tqdm_write  # type: ignore[attr-defined]
    print("Tqdm não encontrado. Instale com 'pip install tqdm' para barra de progresso.")

try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
except Exception:  # pragma: no cover - Interface gráfica nem sempre disponível
    tk = None
    messagebox = None
    simpledialog = None

# Extensões suportadas
SUPPORTED_SUFFIXES = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".csv",
    ".md",
    ".txt",
    ".html",
    ".htm",
    ".xml",
    ".jpg",
    ".jpeg",
    ".png",
    ".tiff",
    ".bmp",
    ".gif",
    ".wav",
    ".mp3",
    ".aac",
    ".flac",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Converter arquivos em lote com Docling")
    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="Arquivo ou diretório que deve ser processado. Diretórios são percorridos recursivamente.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docling-output"),
        help="Diretório onde o Docling deve colocar os artefatos convertidos.",
    )
    parser.add_argument(
        "--to",
        nargs="?",
        default=None,
        help="Formato de saída opcional do Docling (ex: md, json). Usa a configuração padrão do Docling.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Pula o processamento quando o Docling já produziu artefatos para um arquivo.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Imprime stdout/stderr do Docling para cada arquivo processado.",
    )
    return parser.parse_args()


def iter_input_files(source: Path) -> Iterable[Path]:
    if source.is_file():
        yield source
        return

    for path in source.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path


def prompt_for_directory_cli() -> Path:
    while True:
        user_input = input("Qual o caminho do diretório? ").strip()
        if not user_input:
            print(f"{Fore.YELLOW}Um caminho é necessário.{Style.RESET_ALL}")
            continue

        candidate = Path(user_input).expanduser().resolve()
        if candidate.exists():
            return candidate

        print(f"{Fore.RED}O caminho '{candidate}' não existe. Tente novamente.{Style.RESET_ALL}")


def prompt_for_directory_gui() -> Path:
    if tk is None or simpledialog is None:
        return prompt_for_directory_cli()

    root = tk.Tk()
    root.withdraw()

    try:
        selected_path = None
        while selected_path is None:
            user_input = simpledialog.askstring(
                title="Docling",
                prompt="Qual o caminho do diretório?",
                parent=root,
            )

            if user_input is None:
                if messagebox and messagebox.askyesno(
                    title="Encerrar",
                    message="Nenhum diretório informado. Deseja sair?",
                ):
                    raise SystemExit("Nenhum diretório informado.")
                continue

            trimmed_input = user_input.strip()
            if not trimmed_input:
                if messagebox:
                    messagebox.showwarning(
                        title="Entrada vazia",
                        message="Informe um caminho válido.",
                    )
                else:
                    print(f"{Fore.YELLOW}Um caminho é necessário.{Style.RESET_ALL}")
                continue

            candidate = Path(trimmed_input).expanduser().resolve()
            if candidate.exists():
                selected_path = candidate
            else:
                if messagebox:
                    messagebox.showerror(
                        title="Caminho inválido",
                        message=f"O caminho '{candidate}' não existe.",
                    )
                else:
                    print(
                        f"{Fore.RED}O caminho '{candidate}' não existe. Tente novamente.{Style.RESET_ALL}"
                    )

        return selected_path
    finally:
        root.destroy()


def prompt_for_directory() -> Path:
    return prompt_for_directory_gui()


def resolve_source_path(candidate: Path | None) -> Path:
    if candidate is not None:
        return candidate.expanduser().resolve()

    return prompt_for_directory()


def write_failure_report(failed_files: Iterable[Path], output_root: Path) -> Path:
    report_path = output_root / "failed_conversions.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as report_file:
        report_file.write("Arquivos que falharam na conversão:\n")
        for file_path in failed_files:
            report_file.write(f"{file_path}\n")

    tqdm.write(f"{Fore.YELLOW}Relatório de falhas escrito em {report_path}{Style.RESET_ALL}")
    return report_path


def convert_files(
    files: List[Path],
    source: Path,
    output_root: Path,
    output_format: str | None,
    skip_existing: bool,
    verbose: bool,
) -> List[Path]:
    failures: List[Path] = []

    for file_path in tqdm(files, desc="Convertendo", unit="arquivo", ncols=80):
        relative_parent = Path()
        if source.is_dir():
            try:
                relative_parent = file_path.parent.relative_to(source)
            except ValueError:
                relative_parent = Path()

        destination_dir = output_root / relative_parent

        if skip_existing and destination_dir.exists():
            existing_outputs = list(destination_dir.glob(f"{file_path.stem}*"))
            if existing_outputs:
                continue

        ok = run_docling(file_path, destination_dir, output_format, verbose)
        if not ok:
            failures.append(file_path)

    return failures


def run_docling(input_file: Path, output_dir: Path, output_format: str | None, verbose: bool) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["docling"]
    if output_format:
        cmd.extend(["--to", output_format])
    cmd.extend(["--output", str(output_dir), str(input_file)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        tqdm.write(
            f"{Fore.RED}CLI do Docling não encontrado no PATH. Instale o docling e tente novamente.{Style.RESET_ALL}"
        )
        return False

    if verbose:
        if result.stdout:
            tqdm.write(result.stdout.rstrip())
        if result.stderr:
            tqdm.write(result.stderr.rstrip())

    if result.returncode != 0:
        tqdm.write(
            f"{Fore.RED}Docling falhou para {input_file}: código de saída {result.returncode}{Style.RESET_ALL}"
        )
        if not verbose and result.stderr:
            tqdm.write(result.stderr.rstrip())
        return False

    return True


def main() -> int:
    colorama_init(autoreset=True)
    args = parse_args()
    source = resolve_source_path(args.source)
    output_root = args.output.expanduser().resolve()

    if not source.exists():
        print(f"{Fore.RED}Caminho de origem {source} não existe.{Style.RESET_ALL}", file=sys.stderr)
        return 1

    files = list(iter_input_files(source))
    if not files:
        print(f"{Fore.YELLOW}Nenhum arquivo suportado encontrado para processar.{Style.RESET_ALL}")
        return 0

    output_root.mkdir(parents=True, exist_ok=True)

    failures = convert_files(
        files=files,
        source=source,
        output_root=output_root,
        output_format=args.to,
        skip_existing=args.skip_existing,
        verbose=args.verbose,
    )

    if failures:
        report_path = write_failure_report(failures, output_root)
        print(
            f"{Fore.RED}Finalizado com {len(failures)} falha(s). Veja {report_path} para detalhes.{Style.RESET_ALL}",
            file=sys.stderr,
        )
        return 2

    print(f"{Fore.GREEN}Conversão concluída com sucesso.{Style.RESET_ALL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())