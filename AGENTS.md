# Agent Guidelines for Docling Directory Converter

## Build/Test Commands
- **Setup (pip)**: `python3 -m venv .venv && source .venv/bin/activate && pip install docling tqdm colorama`
- **Setup (uv)**: `./run.sh` (auto-installs uv, creates venv, installs deps)
- **Run converter**: `python convert_directory.py /path/to/source --output tmp_output --verbose`
- **Run interactive CLI**: `python interactive_cli.py` or `./run.sh`
- **Lint**: `ruff check .` or `flake8 .`
- **Format**: `ruff format .`
- **Test single file**: `python -m pytest tests/test_convert_directory.py::test_function_name -v` (when tests exist)
- **Test all**: `python -m pytest tests/ -v` (when tests exist)

## Code Style Guidelines
- **Python version**: 3.10+ with `from __future__ import annotations`
- **Imports**: stdlib first, then third-party; use try/except for optional deps (tqdm, colorama)
- **Types**: Use type hints for function parameters and return values
- **Naming**: snake_case for functions/variables, UPPERCASE for constants, descriptive names
- **Error handling**: Try/except with specific exceptions, meaningful error messages with colorama
- **Formatting**: 4-space indentation, 88-char line length, ruff/flake8 compliance
- **Docstrings**: Concise imperative style for functions and modules
- **Language**: Use Portuguese for user-facing messages, English for code/docs
- **Optional dependencies**: Graceful fallbacks when tqdm/colorama unavailable
