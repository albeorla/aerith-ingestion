"""
Command-line interface for Aerith ingestion.
"""

import click
from loguru import logger

from aerith_ingestion.config import AppConfig, load_config
from aerith_ingestion.config.logging import setup_logging


class CommandContext:
    """Context object for CLI commands with shared dependencies."""

    def __init__(self, config: AppConfig):
        self.config = config


pass_context = click.make_pass_decorator(CommandContext)


@click.group()
@click.pass_context
def cli(ctx):
    """Aerith ingestion CLI."""
    # Initialize logging and config
    config = load_config()
    setup_logging(config.logging)
    ctx.obj = CommandContext(config)


from aerith_ingestion.commands.crawl import crawl  # noqa

# Import commands after context setup to avoid circular imports
from aerith_ingestion.commands.sync import sync  # noqa

# Register commands
cli.add_command(sync)
cli.add_command(crawl)


if __name__ == "__main__":
    cli()
