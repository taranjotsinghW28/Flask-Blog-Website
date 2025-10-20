from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Create database globally
db = SQLAlchemy()
login_manager = LoginManager()  # <-- Create LoginManager

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "my_super_secret_key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/blog_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)  # Initialize LoginManager
    login_manager.login_view = 'auth.login'  # default login route
    login_manager.login_message_category = 'info'
    migrate = Migrate(app, db)
    # Import and register blueprints
    from .routes.auth import auth_bp
    from .routes.tasks import post_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)

    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
