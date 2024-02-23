from flask import Flask
from flask_cors import CORS
from .models import db
from .auth_bp import auth
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pesa.db'
    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(auth, url_prefix='/auth')

    return app
