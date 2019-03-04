#! ../env/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from challenge import models
from .api import api

db = SQLAlchemy()

"""
С помощью этого файла мы сможем если надо сконфигурировать master-slave конфигурацию
"""

"""
class RoutingSession(Session):

    def get_bind(self, mapper=None, clause=None):
        return engines['master']
"""
engine = create_engine('sqlite:///../database.db', logging_name="master", echo=True)
Session = scoped_session(sessionmaker(autocommit=True, bind=engine))


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    Arguments:
        object_name: the python path of the config object,
                     e.g. appname.settings.ProdConfig
    """

    app = Flask(__name__)

    app.config.from_object(object_name)

    # initialize SQLAlchemy
    db.init_app(app)

    # register our blueprints
    app.register_blueprint(api)

    return app


env = os.environ.get('APPNAME_ENV', 'dev')
app = create_app('challenge.settings.%sConfig' % env.capitalize())
