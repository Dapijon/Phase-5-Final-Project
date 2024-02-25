from flask import Flask
from flask_cors import CORS
from .models import db
from .auth_bp import auth
from .transactions import transactions_bp 
from flask_migrate import Migrate
from .summary import summary_bp
from .transactions import transactions_bp

def create_app():
    app = Flask(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:3001"}})
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pesa.db'
    app.config['SECRET_KEY']='klfjkldfjdi13kfdl44j4lkj4'
    
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    
    db.init_app(app)
    
    app.register_blueprint(summary_bp, url_prefix='/summary')
    migrate = Migrate(app, db)

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(transactions_bp, url_prefix='/transaction')

    return app
