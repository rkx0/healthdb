from flask import Flask, request, redirect, url_for, render_template, jsonify, session
import json
import os
import uuid

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

# Path to store user data
data_file = 'user_data.json'

def load_data():
    """
    Load user data from the JSON file.
    """
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    """
    Save user data to the JSON file.
    """
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)  # Add indentation for readability

def generate_patient_id():
    """
    Generate a unique patient ID.
    """
    return str(uuid.uuid4())

def get_patient_id(username):
    """
    Get the patient ID based on the username.
    """
    data = load_data()
    if username in data:
        return data[username].get('patient_id')
    return None

@app.route('/', methods=['GET', 'POST'])
def signup():
    """
    User signup route.
    """
    error = None
    data = load_data()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        usertype = request.form.getlist('usertype')  # Use getlist for checkboxes

        if not usertype:
            error = "Please select user type (Patient or Doctor)."
        elif len(usertype) > 1:
            error = "You can only select one user type."
        else:
            usertype = usertype[0]  
            if username in data:
                error = "Username already exists!"
            else:
                patient_id = generate_patient_id()
                data[username] = {'password': password, 'usertype': usertype, 'patient_id': patient_id}
                save_data(data)  
                return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    """
    error = None
    data = load_data()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in data and data[username]['password'] == password:
            session['username'] = username  # Set the username in the session
            patient_id = data[username].get('patient_id')
            if patient_id:
                if os.path.exists(os.path.join('patients', patient_id, 'patient_info.json')):
                    return redirect(url_for('dashboard', patient_id=patient_id))

            return redirect(url_for('add_patient', patient_id=patient_id))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    """
    Route to add patient information.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        country = request.form.get('country')
        city = request.form.get('city')
        patient_id = request.args.get('patient_id')

        if patient_id is None:
            return "Error: Patient ID not provided."

        patient_directory = os.path.join('patients', patient_id)
        if not os.path.exists(patient_directory):
            os.makedirs(patient_directory)

        patient_data = {
            'name': name,
            'age': age,
            'gender': gender,
            'country': country,
            'city': city,
        }
        with open(os.path.join(patient_directory, 'patient_info.json'), 'w') as f:
            json.dump(patient_data, f, indent=4)

        return redirect(url_for('dashboard', patient_id=patient_id))

    return render_template('patient.html')

@app.route('/dashboard')
def dashboard():
    patient_id = request.args.get('patient_id')
    # Check if patient_id is None
    if patient_id is None:
        return "Error: Patient ID not provided."
    # Your dummy dashboard logic (optional)
    return render_template('dashboard.html', patient_id=patient_id)

@app.route('/patients/<patient_id>/patient_info.json')
def serve_patient_info(patient_id):
    """
    Serve patient information JSON files.
    """
    json_file_path = os.path.join('patients', patient_id, 'patient_info.json')
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            patient_info = json.load(f)
            return jsonify(patient_info)
    else:
        return "Error: Patient info not found."

@app.route('/save_patient_data', methods=['POST'])
def save_patient_data():
    """
    Route to save patient information and health data.
    """
    if request.method == 'POST':
        data = request.json
        username = session.get('username')  # Get the username from the session
        patient_id = get_patient_id(username)

        if patient_id is None:
            return jsonify({'error': 'Patient ID not found for this user.'}), 400

        patient_directory = os.path.join('patients', patient_id)
        if not os.path.exists(patient_directory):
            os.makedirs(patient_directory)

        with open(os.path.join(patient_directory, 'health_data.json'), 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({'message': 'Patient information and health data saved successfully.'})

    return jsonify({'error': 'Invalid request method.'})

import os
import json

def save_health_data(patient_id, data):
    """
    Save health data for a patient to a JSON file.
    
    Args:
        patient_id (str): The ID of the patient.
        data (dict): A dictionary containing the health data.
        
    Returns:
        None
    """
    # Define the directory path for the patient
    directory_path = os.path.join('patients', patient_id)
    
    # Create the directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    # Define the file path for the health data JSON file
    file_path = os.path.join(directory_path, 'health_data.json')
    
    # Save the health data to the JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    app.run(debug=True)
