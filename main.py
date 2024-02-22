from app import create_app
from flask import request



app = create_app()

@app.route('/')
def index():
    return 'Welcome to Pesa App'


if __name__ == '__main__':
    app.run(debug=True)