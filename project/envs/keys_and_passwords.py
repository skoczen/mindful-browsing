AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None
AWS_STORAGE_BUCKET_NAME = None
DB_PASSWORD = None
GAUGES_SITE_ID = None
GOOGLE_ANALYTICS_PROPERTY_ID = None
INTERCOM_APP_ID = None

try:
    from keys_and_passwords_private import *
except:
    pass

from os import environ

def set_env_fallback(key):

    if (key not in globals() or globals()[key] is None) and key in environ:
        globals()[key] = environ[key]

set_env_fallback("AWS_ACCESS_KEY_ID")
set_env_fallback("AWS_SECRET_ACCESS_KEY")
set_env_fallback("AWS_STORAGE_BUCKET_NAME")
set_env_fallback("DB_PASSWORD")
set_env_fallback("GAUGES_SITE_ID")
set_env_fallback("GOOGLE_ANALYTICS_PROPERTY_ID")
set_env_fallback("INTERCOM_APP_ID")
