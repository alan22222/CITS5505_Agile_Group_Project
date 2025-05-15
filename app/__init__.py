
import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from dotenv import load_dotenv


db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object('config.Config')
#     app.config['SECRET_KEY'] = 'devkey'
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#     db.init_app(app)
#     csrf.init_app(app)
#     migrate.init_app(app, db)
#     login_manager.init_app(app)
#     login_manager.login_view = 'main.login'

#     from app.models import User  # after app setup to avoid circular import
#     from app.routes import main
#     app.register_blueprint(main)

#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.query.get(int(user_id))


#     return app

def create_app(config_class=None):

    load_dotenv()
    
    app = Flask(__name__)
    # 从 .env 文件中获取 SECRET_KEY，并覆盖配置中的值
    secret_key = os.environ.get('SECRET_KEY')
    # Load test config if passed in, otherwise default to 'config.Config'
    if config_class is None:
        app.config.from_object('config.Config')
    else:
        app.config.from_object(config_class)

    # You can still override this below if needed
    # Yanchen: I am trying to modify this in order to retrieve key from .env file, thus I need to comment the following line
    # app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'devkey')
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///database.db')

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.models import User  # Avoid circular import
    from app.routes import main
    app.register_blueprint(main)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

    