import os
from re import A

class Config:
    SECRET_KEY = os.urandom(16)
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://server_223:!QAZ2wsx@10.7.6.199/handover?charset=utf8mb4'
    SQLALCHEMY_POOL_SIZE = 50
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
    'toHandover': 'mysql+mysqlconnector://server_223:!QAZ2wsx@10.7.6.199/handover?charset=utf8mb4',
    'toDHS': 'mysql+mysqlconnector://server_223:!QAZ2wsx@10.7.6.199/dhs?charset=utf8mb4'
    }
    
    MAIL_SERVER='smtp-yt.infra.prod'
    MAIL_PORT=25
    MAIL_USE_SSL=False
    # MAIL_USERNAME = 'dhs.ytops@gmail.com'
    # MAIL_PASSWORD = '!QAZ2wsx3edc`'
    
    # MAIL_SERVER='smtp.gmail.com'
    # MAIL_PORT=465
    # MAIL_USE_SSL=True
    # MAIL_USERNAME = 'dhs.ytops@gmail.com'
    # MAIL_PASSWORD = '!QAZ2wsx3edc`'
    
    # MAIL_SERVER='smtp.gmail.com'
    # MAIL_PORT=465
    # MAIL_USE_SSL=True
    # MAIL_USERNAME = 'ytops.alerts@gmail.com'
    # MAIL_PASSWORD = '0984@Xy188$%^'
    
class ProdConfig(Config):
    DEBUG = False


class DevConfig(Config):
    DEBUG = True