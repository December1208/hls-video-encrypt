from app import app


def async_task(func):

    def wrapper(*args, **kwargs):

        with app.app_context():
            result = func(*args, **kwargs)

        return result

    return wrapper


