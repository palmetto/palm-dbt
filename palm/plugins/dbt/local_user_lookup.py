import os


def local_user_lookup() -> str:
    user = "no_user"
    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user_found = os.environ.get(name)
        if user_found:
            user = user_found
    return user
