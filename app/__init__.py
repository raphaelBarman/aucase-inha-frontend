import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        ELASTICSEARCH_URL= 'http://localhost:9200',
        SECRET_KEY = 'dev',
        SQLALCHEMY_DATABASE_URI = 'mysql://test:1234@localhost/aucase?unix_socket=/run/mysqld/mysqld.sock&charset=utf8',
        JSON_AS_ASCII = False
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('./config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    db.init_app(app)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
