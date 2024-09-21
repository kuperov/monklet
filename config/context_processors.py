# def language_code(request):
#     return {"LANGUAGE_CODE": request.LANGUAGE_CODE}


# def get_cookie(request):
#     return {"COOKIES": request.COOKIES}


# # Add the 'ENVIRONMENT' setting to the template context
# def environment(request):
#     return {"ENVIRONMENT": settings.ENVIRONMENT}


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
