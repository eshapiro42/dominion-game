from os import environ
from dotenv import load_dotenv


load_dotenv()


class Config:
    ENV = environ.get("ENV")
    DEBUG = environ.get("DEBUG")
    SECRET_KEY = environ.get("SECRET_KEY")
