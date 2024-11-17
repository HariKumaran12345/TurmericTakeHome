from twilio.rest import Client 
from flask import Flask, after_this_request, render_template, request, jsonify, send_file, redirect, url_for, session
from twilio.twiml.messaging_response import MessagingResponse
from export import export_csv, export_excel, export_google_sheets
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv


# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session handling

#Credentials loaded (specify these in a .env file)
load_dotenv()
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
secret_key = os.getenv('ENCRYPTION_KEY')
PASSWORD = os.getenv('ADMIN_PASSWORD', 'default_password') #can change or set this password for specific organizations

client = Client(account_sid, auth_token)

#Encrpyion setup
cipher = Fernet(secret_key)

def encrypt_data(data):
    """Encrypt data using Fernet symmetric encryption."""
    return cipher.encrypt(data.encode())

def decrypt_data(encrypted_data):
    """Decrypt data using Fernet symmetric encryption."""
    return cipher.decrypt(encrypted_data).decode()

# Patient data storage (encrypted)
patient_data = {}

#Main bot functionality, in charge of collecting personal information
@app.route("/webhook", methods=["POST"])
def webhook():
    message = request.form.get('Body').strip().lower()
    from_number = request.form.get('From')
    response = MessagingResponse()
    
    if from_number not in patient_data:
        response.message("Hi! I'm a bot in charge of collecting your information and securely exporting it to proper digital formats. To start, please state your full name.")
        patient_data[from_number] = {
            'name': None,
            'dob': None,
            'gender': None,
            'address': None,
            'medical_history': None,
            'current_medications': None
        }
    else:
        if patient_data[from_number]['name'] is None:
            patient_data[from_number]['name'] = encrypt_data(message)
            response.message("Got it. What is your date of birth? Please enter in MM/DD/YYYY format")
        elif patient_data[from_number]['dob'] is None:
            patient_data[from_number]['dob'] = encrypt_data(message)
            response.message("Understood, what is your gender?")
        elif patient_data[from_number]['gender'] is None:
            patient_data[from_number]['gender'] = encrypt_data(message)
            response.message("Next, what is your address? ")
        elif patient_data[from_number]['address'] is None:
            patient_data[from_number]['address'] = encrypt_data(message)
            response.message("Perfect, now could you briefly describe your medical history (e.g., allergies, previous surgeries). Enter N/A if you don't have a significant history.")
        elif patient_data[from_number]['medical_history'] is None:
            patient_data[from_number]['medical_history'] = encrypt_data(message)
            response.message("Finally, what are your current medications? Please enter N/A if you don't take any.")
        elif patient_data[from_number]['current_medications'] is None:
            patient_data[from_number]['current_medications'] = encrypt_data(message)
            response.message("Thank you! Your information has been saved.")
    
    return str(response)

@app.route("/export_csv/<phone>", methods=["POST"])
def export_single_csv(phone):
    app.logger.info(f"Export CSV request received for phone: {phone}")
    
    try:
        if phone not in patient_data:
            app.logger.error(f"Phone {phone} not found in patient_data")
            return jsonify({"error": "Patient not found"}), 404
        
        # Decrypt single patient data
        decrypted_data = {
            phone: {k: decrypt_data(v) if v else v for k, v in patient_data[phone].items()}
        }
        
        tmp_path, filename = export_csv(decrypted_data)
        if tmp_path is None:
            return jsonify({"error": filename}), 500
        
        @after_this_request
        def cleanup(response):
            try:
                os.remove(tmp_path)
            except Exception as e:
                app.logger.error(f"Cleanup error: {e}")
            return response
        
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        app.logger.error(f"Export error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/export_excel/<phone>", methods=["POST"])
def export_single_excel(phone):
    try:
        if phone not in patient_data:
            return jsonify({"error": "Patient not found"}), 404
        
        # Decrypt single patient data
        decrypted_data = {
            phone: {k: decrypt_data(v) if v else v for k, v in patient_data[phone].items()}
        }
        
        tmp_path, filename = export_excel(decrypted_data)
        if tmp_path is None:
            return jsonify({"error": filename}), 500
        
        @after_this_request
        def cleanup(response):
            try:
                os.remove(tmp_path)
            except Exception as e:
                app.logger.error(f"Cleanup error: {e}")
            return response
        
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/export_google_sheets/<phone>", methods=["POST"])
def export_single_google_sheets(phone):
    try:
        credentials_json = request.form.get('credentials')
        if not credentials_json:
            return jsonify({"error": "Google credentials required"}), 400
        
        if phone not in patient_data:
            return jsonify({"error": "Patient not found"}), 404
        
        # Decrypt single patient data
        decrypted_data = {
            phone: {k: decrypt_data(v) if v else v for k, v in patient_data[phone].items()}
        }
        
        result = export_google_sheets(decrypted_data, credentials_json)
        if result.startswith("Error"):
            return jsonify({"error": result}), 500
            
        return jsonify({"url": result})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('view_data'))
        else:
            error = "Invalid password. Please try again."
    return '''
        <form method="post">
            <label for="password">Enter Password:</label>
            <input type="password" id="password" name="password">
            <button type="submit">Login</button>
            <p style="color: red;">{}</p>
        </form>
    '''.format(error if error else '')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    #return "Logged out successfully."
    return redirect(url_for('login'))  # Redirect to the login page

# Other routes (webhook, export, etc.) remain unchanged, but add the following:
def login_required(f):
    def wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapped.__name__ = f.__name__
    return wrapped

@app.route("/view_data", methods=["GET"])
@login_required
def view_data():
    # Decrypt data before rendering
    decrypted_data = {
        phone: {k: decrypt_data(v) if v else v for k, v in data.items()}
        for phone, data in patient_data.items()
    }
    return render_template("view_data.html", patient_data=decrypted_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
