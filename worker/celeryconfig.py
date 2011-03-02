BROKER_HOST = "broker.spell.dotcloud.com"
BROKER_PORT = 4242
BROKER_USER = "lolita"
BROKER_PASSWORD = "InYourAss"
CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ('wordcounter', 'spellchecker')
CELERY_DISABLE_RATE_LIMITS = True
