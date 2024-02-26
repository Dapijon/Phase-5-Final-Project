from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    form_data = request.get_json()
    
    updated_user = {
        'firstName': form_data['firstName'],
        'lastName': form_data['lastName'],
        'email': form_data['email'],
        'profileImage': form_data['profileImage'],
    }

    return jsonify(updated_user)

if __name__ == '__main__':
    app.run()