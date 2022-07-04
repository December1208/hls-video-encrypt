from app import app


def async_task(func):

    async def wrapper(*args, **kwargs):

        with app.app_context():
            result = await func(*args, **kwargs)

        return result

    return wrapper


