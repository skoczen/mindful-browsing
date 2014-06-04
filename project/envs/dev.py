from envs.common import *

if False:
    MIDDLEWARE_CLASSES =  (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ) + MIDDLEWARE_CLASSES

    

    INSTALLED_APPS += ("debug_toolbar", )

INTERNAL_IPS = ('127.0.0.1',)

# Uncomment to turn on intercom
# ANALYTICAL_INTERNAL_IPS = []
