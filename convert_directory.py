#!/usr/bin/env python3
"""Batch conversion helper for Docling.

This script walks a directory (recursively) and invokes the globally installed
`docling` CLI for every supported file it finds. The goal is to make it easy to
pipe a knowledge base or any document tree into Docling without having to
manually iterate over files.

Usage example:
    python convert_directory.py /path/to/source --output /path/to/output

By default the script mirrors the directory structure under the chosen output
root so that Docling's artefacts remain grouped by their originating folder.
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
        print("colorama não encontrado. Instale com 'pip install colorama' para saída colorida.")

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover - fallback for environments without tqdm
    def tqdm(iterable, *_, **__):  # type: ignore
        for item in iterable:
            yield item

    def _tqdm_write(message: str) -> None:
        print(message)

    tqdm.write = _tqdm_write  # type: ignore[attr-defined]
    print("tqdm não encontrado. Instale com 'pip install tqdm' para barra de progresso.")

try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
except Exception:  # pragma: no cover - GUI not always available
    tk = None
    messagebox = None
    simpledialog = None

# Docling supports several input families. The CLI autodetects formats, so the
# list below mainly filters out obvious non-document artefacts (e.g. binaries
# with extensions Docling cannot parse). Extend the list if your workload
# contains additional suffixes handled by Docling.
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
    parser = argparse.ArgumentParser(description="Batch convert files with Docling")
    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="File or directory that should be processed. Directories are traversed recursively.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docling-output"),
        help="Directory where Docling should place converted artefacts.",
    )
    parser.add_argument(
        "--to",
        nargs="?",
        default=None,
        help="Optional Docling output format (e.g. md, json). Defaults to Docling's standard setting.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip processing when Docling already produced artefacts for a file.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print Docling's stdout/stderr for each processed file.",
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
        user_input = input("Qual caminho do diretório? ").strip()
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
    selected_path: Path | None = None

    try:
        while selected_path is None:
            user_input = simpledialog.askstring(
                title="Docling",
                prompt="Qual caminho do diretório?",
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
        report_file.write("Files that failed conversion:\n")
        for file_path in failed_files:
            report_file.write(f"{file_path}\n")

    tqdm.write(f"{Fore.YELLOW}Failure report written to {report_path}{Style.RESET_ALL}")
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

    for file_path in tqdm(files, desc="Converting", unit="file", ncols=80):
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
            f"{Fore.RED}Docling CLI was not found on PATH. Install docling and retry.{Style.RESET_ALL}"
        )
        return False

    if verbose:
        if result.stdout:
            tqdm.write(result.stdout.rstrip())
        if result.stderr:
            tqdm.write(result.stderr.rstrip())

    if result.returncode != 0:
        tqdm.write(
            f"{Fore.RED}Docling failed for {input_file}: exit code {result.returncode}{Style.RESET_ALL}"
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
        print(f"{Fore.RED}Source path {source} does not exist.{Style.RESET_ALL}", file=sys.stderr)
        return 1

    files = list(iter_input_files(source))
    if not files:
        print(f"{Fore.YELLOW}No supported files found to process.{Style.RESET_ALL}")
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
            f"{Fore.RED}Finished with {len(failures)} failure(s). See {report_path} for details.{Style.RESET_ALL}",
            file=sys.stderr,
        )
        return 2

    print(f"{Fore.GREEN}Conversion completed successfully.{Style.RESET_ALL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
