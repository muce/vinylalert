from flask import Flask
from flask_oauth import OAuth
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
oauth = OAuth()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    discogs = oauth.remote_app(
        'discogs',
        base_url = app.config["DISCOGS_BASE_URL"],
        request_token_url = app.config["DISCOGS_REQUEST_TOKEN_URL"], 
        access_token_url = app.config["DISCOGS_ACCESS_TOKEN_URL"],
        authorize_url = app.config["DISCOGS_AUTHORIZE_URL"],
        consumer_key = 'RFTnVYOtuadvJqIpwdrh',
        consumer_secret = 'QIpGQsrKfynHndnXYYjMuIqnUBfGAREi'
    )
    
    print 'discogs object: '+str(discogs)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
