#!/usr/bin/env python
"""Main CLI entrypoint for the presentation app."""
import importlib
import pkgutil
from pathlib import Path

import asyncclick as click

from app.infrastructure.app import init_di


COMMANDS_DIR = Path(__file__).parent / "app" / "presentation" / "cli"


@click.group()
def main():
    """Main CLI group"""
    pass


def load_commands():
    """Dynamically load all commands from the commands directory."""

    for module_info in pkgutil.iter_modules([str(COMMANDS_DIR)]):
        module = importlib.import_module(f"app.presentation.cli.{module_info.name}")

        for item in dir(module):
            obj = getattr(module, item)
            if isinstance(obj, click.core.Command):
                main.add_command(obj)


# Initialize the DI container
init_di()

# Load commands before running the main CLI
load_commands()

if __name__ == "__main__":
    main()  # _anyio_backend="trio"
