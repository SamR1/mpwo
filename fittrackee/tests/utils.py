from json import dumps
from typing import Dict, Optional, Union
from uuid import uuid4

from requests import Response


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


def generate_response(
    content: Optional[Union[str, Dict]] = None,
    status_code: Optional[int] = None,
) -> Response:
    content = content if content else {}
    response = Response()
    response._content = (
        dumps(content).encode()
        if isinstance(content, dict)
        else content.encode()
    )
    response.status_code = status_code if status_code else 200
    return response
