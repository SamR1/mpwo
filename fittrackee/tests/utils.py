from uuid import uuid4


def random_domain() -> str:
    return f'https://{uuid4().hex}.social'
