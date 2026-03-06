from django.conf import settings


def _random_string(length):
    import random
    import string
    import time

    random.seed(time.time())
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


CACHE_BUSTER = _random_string(length=10)


def cache_buster(_request):
    return dict(CACHE_BUSTER=CACHE_BUSTER)


def account_settings(_request):
    return {
        "ACCOUNT_ALLOW_REGISTRATION": getattr(
            settings, "ACCOUNT_ALLOW_REGISTRATION", True
        )
    }
