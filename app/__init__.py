from flask import Flask
from config import Config 
from flask_login import LoginManager #to log users in and out and maintain the session
from flask_sqlalchemy import SQLAlchemy #this talk to the database
from flask_migrate import Migrate #this makes altering the db a lot easier
from flask_moment import Moment




login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'You must be logged in to view this page.'
login.login_message_category = "warning"

db = SQLAlchemy()

migrate = Migrate()
moment = Moment()

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)

    from .blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .blueprints.social import bp as social_bp
    app.register_blueprint(social_bp)
    
    return app

