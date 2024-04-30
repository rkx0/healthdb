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

        # Check if the username exists and matches the provided password
        if username in data and data[username]['password'] == password:
            # Check if the user has a patient ID
            patient_id = data[username].get('patient_id')
            if patient_id:
                # Check if the patient info JSON file exists
                if os.path.exists(os.path.join('patients', patient_id, 'patient_info.json')):
                    return redirect(url_for('dashboard', patient_id=patient_id))

            # If patient info JSON file doesn't exist, redirect to add_patient route
            return redirect(url_for('add_patient', patient_id=patient_id))
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
        patient_id = request.args.get('patient_id')

        # Check if patient_id is None
        if patient_id is None:
            return "Error: Patient ID not provided."

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

        # Redirect to dashboard with patient_id
        return redirect(url_for('dashboard', patient_id=patient_id))

    return render_template('patient.html')

@app.route('/dashboard')
def dashboard():
    patient_id = request.args.get('patient_id')
    # Your dummy dashboard logic (optional)
    return render_template('dashboard.html', patient_id=patient_id)  # Render dashboard template (if needed)

if __name__ == "__main__":
    # Run the app, binding to all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)