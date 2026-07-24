# Tests and static checks

Run the commands below from the repository root after installing the project
dependencies.

## Automated tests

Run the complete test suite:

```bash
python -m unittest discover -s tests -q
```

Run the complete suite with the name and result of every test:

```bash
python -m unittest discover -s tests -v
```

Run only the UI tests:

```bash
python -m unittest discover -s tests -p 'test_*_ui.py' -v
```

Run one test module directly:

```bash
python tests/test_about_settings_ui.py -v
```

The shared Qt test setup automatically:

- uses the local repository instead of an installed ZapZap version;
- selects the Qt `offscreen` platform when no platform was specified;
- keeps a single `QApplication` instance alive;
- stores test data, settings and cache in a temporary directory.

UI tests are automated assertions and do not open an interactive window.

## Static unused-code and package checks

Check for probably unused imports, variables, attributes, methods and classes,
and also compare Python package directories with
`tool.setuptools.packages` in `pyproject.toml`:

```bash
python tests/check_unused_code.py
```

The command returns a non-zero status when it finds candidates. To print the
inventory without failing:

```bash
python tests/check_unused_code.py --no-fail
```

Check only whether packages were added to or removed from
`pyproject.toml` correctly:

```bash
python tests/check_unused_code.py --packages-only
```
