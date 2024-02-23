from flask import Flask
from flask_cors import CORS
from .models import db
from .auth_bp import auth
from flask_migrate import Migrate
from .summary import summary_bp

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pesa.db'
    app.config['SECRET_KEY']='klfjkldfjdi13kfdl44j4lkj4'
    
    db.init_app(app)
    
    app.register_blueprint(summary_bp)
    migrate = Migrate(app, db)

    app.register_blueprint(auth, url_prefix='/auth')

    return app
