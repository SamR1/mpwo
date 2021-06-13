from typing import Optional
from uuid import uuid4


def random_uuid() -> str:
    return uuid4().hex


def random_string(
    prefix: Optional[str] = None, suffix: Optional[str] = None
) -> str:
    return (
        f'{"" if prefix is None else prefix}'
        f'{random_uuid()}'
        f'{"" if suffix is None else suffix}'
    )


def random_domain() -> str:
    return random_string(prefix='https://', suffix='.social')
