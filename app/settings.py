import json
import os

import dotenv

dotenv.load_dotenv(verbose=True)


def parse_str(key, default_value):
    env_value = os.environ.get(key, default_value)
    return env_value


def parse_list(key, default_value):
    env_value = os.environ.get(key, '')
    value = env_value.split(',') or default_value
    return value


def parse_set(key, default_value):
    return set(parse_list(key, default_value))


def parse_dict(key, default_value):
    env_value = os.environ.get(key, '{}')
    value = json.loads(env_value) or default_value
    return value


def parse_bool(key, default_value):
    return bool(parse_int(key, default_value))


def parse_int(key, default_value):
    env_value = os.environ.get(key)
    if env_value is None:
        return default_value
    value = int(env_value)
    return value


def load_setting_value(field, field_type, default_value):
    valid_field_type_to_parse_func = {
        str: parse_str,
        list: parse_list,
        set: parse_set,
        dict: parse_dict,
        bool: parse_bool,
        int: parse_int,
    }

    parse_func = valid_field_type_to_parse_func.get(field_type)
    if parse_func is None:
        raise Exception(
            f"unsupported field type {field_type}, only support field type {valid_field_type_to_parse_func.keys()}"
        )
    value = parse_func(field, default_value)
    return value


class Setting(object):

    FLASK_ENV = load_setting_value('FLASK_ENV', str, 'production')
    SECRET_KEY = load_setting_value('SECRET_KEY', str, '45008b73ad9d00c01f174dddd41df6ad')
    TESTING = load_setting_value('TESTING', bool, False)

    SENTRY_URI = load_setting_value('SENTRY_URI', str, '')
    SERVER_HOST = load_setting_value('SERVER_HOST', str, 'http://127.0.0.1:5000/')

    JWT_SECRET_KEY = load_setting_value('JWT_SECRET_KEY', str, 'ddfaac4a33c94806')
    JWT_TOKEN_LOCATION = load_setting_value('JWT_TOKEN_LOCATION', list, ['headers'])
    JWT_QUERY_STRING_NAME = load_setting_value('JWT_QUERY_STRING_NAME', str, 'token')
    JWT_QUERY_STRING_VALUE_PREFIX = load_setting_value('JWT_QUERY_STRING_VALUE_PREFIX', str, '')
    JWT_ACCESS_TOKEN_EXPIRES = load_setting_value('JWT_ACCESS_TOKEN_EXPIRES', int, 60 * 5)
    JWT_REFRESH_TOKEN_EXPIRES = load_setting_value('JWT_REFRESH_TOKEN_EXPIRES', int, 60 * 60 * 24 * 7)
    SQLALCHEMY_DATABASE_URI = load_setting_value(
        'SQLALCHEMY_DATABASE_URI', str, ''
    )
    SQLALCHEMY_ENGINE_OPTIONS = load_setting_value(
        'SQLALCHEMY_ENGINE_OPTIONS', dict, {'pool_size': 10, 'pool_recycle': 3600}
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = load_setting_value('SQLALCHEMY_TRACK_MODIFICATIONS', bool, False)
    TEST_DATA_PATH = load_setting_value('TEST_DATA_PATH', str, 'sample_data')

    ORIGIN_MEDIA_PATH = load_setting_value('MEDIA_PATH', str, 'static/origin_media/')
    ENCRYPT_MEDIA_PATH = load_setting_value('ENCRYPT_MEDIA_PATH', str, 'static/encrypt_media')
    STORAGE_BACKEND = load_setting_value('STORAGE_BACKEND', str, 'app.storage_backends.local_backend.LocalBackend')

    # celery 配置
    CELERY_BROKER_URL = load_setting_value('CELERY_BROKER_URL', str, 'redis://localhost:6379/2')
    CELERY_RESULT_BACKEND = load_setting_value('CELERY_RESULT_BACKEND', str, 'redis://localhost:6379/3')
    DEFAULT_CELERY_MAX_RETRIES = load_setting_value('DEFAULT_CELERY_MAX_RETRIES', int, 3)


setting = Setting()
