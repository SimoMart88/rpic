from pathlib import Path

import djclick as click
from django.core.management import call_command

@click.command()
@click.option('--check-deploy', is_flag=True)
@click.argument('admin-user', envvar='DJANGO_SUPERUSER_USERNAME', type=str, default='admin')
@click.argument('admin-email', envvar='DJANGO_SUPERUSER_EMAIL', type=str)
@click.argument('admin-password', envvar='DJANGO_SUPERUSER_PASSWORD', type=str)
@click.argument('verbosity', type=click.IntRange(0, 3), default=1)
def command(check_deploy: bool, admin_user: str, admin_email: str, admin_password: str, verbosity: int) -> None:
    from django.conf import settings
    from django.contrib.auth import get_user_model

    User = get_user_model()

    extra = {
        'verbosity': verbosity,
    }

    click.secho(f"==> Run checks (deploy: {check_deploy}) <==")
    call_command("check", deploy=check_deploy, **extra)

    click.secho("==> Run collectstatic <==")
    static_root = Path(str(settings.STATIC_ROOT))
    if not static_root.exists():
        if verbosity >= 1:
            click.secho(f"- Static root does not exist: {static_root}", fg='yellow')
        static_root.mkdir(parents=True)
    call_command("collectstatic", interactive=False, **extra)

    click.secho("==> Run migrations <==")
    call_command("migrate", **extra)

    click.secho("==> Remove stale contenttypes <==")
    call_command("remove_stale_contenttypes", **extra)

    click.secho("==> Check admin user availability <==")
    if User.objects.filter(username=admin_user).exists():
        if verbosity >= 1:
            click.secho(f"- User '{admin_user}' found, skip creation", fg='green')
    else:
        if verbosity >= 1:
            click.secho(f"- User '{admin_user}' NOT found, trigger creation", fg='yellow')

        call_command(
            "createsuperuser",
            email=admin_email,
            username=admin_user,
            interactive=False,
            **extra
        )

    click.secho("==> Run compressor <==")
    call_command("compress", force=True, **extra)

    click.secho("==> Run System Monitor setup <==")
    call_command("system_monitor_setup", **extra)
