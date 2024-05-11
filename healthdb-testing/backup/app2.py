from flask import Flask, request, redirect, url_for, render_template
import json

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
                # Store password in plain text (UNSAFE)
                data[username] = {'password': password, 'usertype': usertype}
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
            # Login successful
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    # Your dummy dashboard logic (optional)
    return render_template('dashboard.html')  # Render dashboard template (if needed)


if __name__ == '__main__':
    app.run(debug=True)
