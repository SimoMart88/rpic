import djclick as click

from rpi_controller.monitoring import monitors


@click.command()
@click.argument('verbosity', type=click.IntRange(0, 3), default=1)
def command(verbosity: int) -> None:
    for monitor_name, _ in monitors.settings.items():
        if verbosity >= 1:
            click.secho(f"Run setup for monitor '{monitor_name}'", fg='green')
        monitors[monitor_name].setup()
