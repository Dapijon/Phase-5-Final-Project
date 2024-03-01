from flask import Flask
import os
from flask_cors import CORS
from flask_login.login_manager import LoginManager
from flask_jwt_extended import JWTManager
from .models import db, User
from .auth_bp import auth
from .transactions import transactions_bp 
from flask_migrate import Migrate
from .summary import summary_bp

def create_app():
    app = Flask(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pesa.db'
    app.config['SECRET_KEY'] = 'klfjkldfjdi13kfdl44j4lkj4'
    
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    jwt= JWTManager(app)
    
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.register_blueprint(summary_bp, url_prefix='/summary')
    migrate = Migrate(app, db)

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(transactions_bp, url_prefix='/transaction')

    return app
