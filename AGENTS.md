# Agent Guidelines for Docling Directory Converter

## Build/Test Commands
- **Setup**: `python3 -m venv .venv && source .venv/bin/activate && pip install docling tqdm colorama`
- **Run converter**: `python convert_directory.py /path/to/source --output tmp_output --verbose`
- **Lint**: `ruff check .` or `flake8 .`
- **Format**: `ruff format .`
- **Test single file**: `python -m pytest tests/test_convert_directory.py::test_function_name -v`
- **Test all**: `python -m pytest tests/ -v`

## Code Style Guidelines
- **Python version**: 3.10+ with `from __future__ import annotations`
- **Imports**: stdlib first, then third-party; use try/except for optional deps (tqdm, colorama)
- **Types**: Use type hints for function parameters and return values
- **Naming**: snake_case for functions/variables, UPPERCASE for constants, descriptive names
- **Error handling**: Try/except with specific exceptions, meaningful error messages with colorama
- **Formatting**: 4-space indentation, 88-char line length, ruff/flake8 compliance
- **Docstrings**: Concise imperative style for functions and modules
