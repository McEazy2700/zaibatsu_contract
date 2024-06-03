from decouple import config


def unwrap_env_var(name: str) -> str:
    value = config(name)
    if value is None:
        raise ValueError(f"{name} environment variable is not set")
    return str(value)
