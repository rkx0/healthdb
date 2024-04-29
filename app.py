from flask import Flask, request, redirect, url_for, render_template
import json
import os
import uuid

# Path to your external JSON file (replace with your actual path)
data_file = 'user_data.json'

def load_data():
    """
    This function loads user data from the JSON file.
    """
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    """
    This function saves user data to the JSON file.
    """
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)  # Add indentation for readability

# Function to generate patient ID
def generate_patient_id():
    return str(uuid.uuid4())

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def signup():
    error = None  # Initialize error message
    data = load_data()  # Load data before processing signup

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        usertype = request.form.getlist('usertype')  # Use getlist for checkboxes

        # Check usertype and insert into data dictionary
        if not usertype:
            error = "Please select user type (Patient or Doctor)."
        elif len(usertype) > 1:
            error = "You can only select one user type."
        else:
            usertype = usertype[0]  # Get the selected user type
            if username in data:
                error = "Username already exists!"
            else:
                # Generate patient ID
                patient_id = generate_patient_id()
                # Store password in plain text (UNSAFE)
                data[username] = {'password': password, 'usertype': usertype, 'patient_id': patient_id}
                save_data(data)  # Save updated data
                return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    data = load_data()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in data and data[username]['password'] == password:
            # Check if patient JSON exists
            patient_id = data[username].get('patient_id')
            if not patient_id or not os.path.exists(f'patient_{patient_id}.json'):
                return redirect(url_for('add_patient'))  # Redirect to add_patient route

            return redirect(url_for('dashboard'))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        country = request.form.get('country')
        city = request.form.get('city')
        username = request.form.get('username')

        # Load user data
        data = load_data()

        # Get patient ID from user data
        user_data = data.get(username, {})
        patient_id = user_data.get('patient_id')

        if not patient_id:
            # Generate patient ID if not already present
            patient_id = generate_patient_id()
            # Update user data with generated patient ID
            data[username] = {'password': data.get(username, {}).get('password'), 'usertype': data.get(username, {}).get('usertype'), 'patient_id': patient_id}
            save_data(data)

        # Create directory for patient if not exists
        patient_directory = os.path.join('patients', patient_id)
        if not os.path.exists(patient_directory):
            os.makedirs(patient_directory)

        # Save patient information to a new patient JSON
        patient_data = {
            'name': name,
            'age': age,
            'gender': gender,
            'country': country,
            'city': city,
        }
        with open(os.path.join(patient_directory, 'patient_info.json'), 'w') as f:
            json.dump(patient_data, f, indent=4)

        return redirect(url_for('dashboard'))

    return render_template('patient.html')

@app.route('/dashboard')
def dashboard():
    # Your dummy dashboard logic (optional)
    return render_template('dashboard.html')  # Render dashboard template (if needed)

if __name__ == '__main__':
    app.run(debug=True)