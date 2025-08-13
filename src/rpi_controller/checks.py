import typing

from django.core.checks import Error

if typing.TYPE_CHECKING:
    from django.apps import AppConfig


def check_required_env_vars(app_configs: list["AppConfig"], **kwargs: typing.Any) -> list[Error]:
    from rpi_controller.config.settings import env, _MANDATORY_ENV_VARS

    errors = []
    for env_var_name in _MANDATORY_ENV_VARS:
        env_default_value = env.scheme[env_var_name][1]
        if env(env_var_name) == env_default_value:  # Check if is still the default value
            errors.append(
                Error(
                    f"{env_var_name} environment variable is not set properly, "
                    f"default value is still used: '{env_default_value}'.",
                    hint=f"Set the {env_var_name} environment variable properly.",
                    obj=env,
                    id="environ.E001",
                )
            )
    return errors
