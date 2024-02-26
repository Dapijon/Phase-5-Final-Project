from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    form_data = request.get_json()
    
   

if __name__ == '__main__':
    app.run()