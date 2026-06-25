# Contributing

This guide explains how to report issues, prepare local changes and submit pull
requests for ZapZap.

## Reporting issues

Use the GitHub issue tracker for reproducible bugs and focused feature requests:

- Search existing issues before opening a new one.
- Include the ZapZap version and package format.
- Include the operating system, desktop environment and display server when relevant.
- Attach terminal output when startup, packaging or dependency errors are involved.
- For webview issues, mention whether the problem also appears in a regular browser.

## Submitting pull requests

- Keep pull requests focused on one logical change.
- Describe the affected platform, package format or application area.
- Link related issues when applicable.
- Update documentation when behavior, commands or package support changes.
- Avoid committing generated build directories such as `dist/`, `build/` or temporary
  packaging work directories.

## Coding style

- Use concise Python code that follows the existing service/controller structure.
- Keep UI orchestration in `zapzap/controllers/` and reusable behavior in
  `zapzap/services/`.
- Keep Qt Designer source files in `zapzap/ui/` synchronized with generated files in
  `zapzap/views/` when UI changes require regenerated Python code.
- Do not add broad exception handling around imports.
- Prefer explicit names for settings and service methods.

## Development workflow

```bash
git clone https://github.com/rafatosta/zapzap.git
cd zapzap
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python run.py --local
```

See [Development](docs/development.md) for details about requirements and build commands.

## Local testing

Run the workflows affected by your change:

```bash
python run.py --local
```

For packaging changes, run the relevant builder or manifest validation for the package
format you changed. See [Packaging](docs/packaging.md).

## Related documentation

- [Development](docs/development.md)
- [Packaging](docs/packaging.md)
- [Troubleshooting](docs/troubleshooting.md)
