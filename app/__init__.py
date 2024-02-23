from flask import Flask
from .models import db
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pesa.db'
    app.config['SECRET_KEY']='klfjkldfjdi13kfdl44j4lkj4'
    
    db.init_app(app)
    
    app.register_blueprint(summary_bp)
    migrate = Migrate(app, db)
    
    
    
    return app
