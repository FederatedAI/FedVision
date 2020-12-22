We use [black](https://github.com/psf/black) and [flake8](https://github.com/PyCQA/flake8)
to format codes in `fedvision`. For developer, it's quiet easy to install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

This will check code style of changed files before you push codes. 