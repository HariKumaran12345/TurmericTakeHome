from twilio.rest import Client 
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse

# Initialize Flask app
app = Flask(__name__)

# Twilio credentials
account_sid = 'AC12b3702342fcf2bc6d7ee41eeef9fecc'
auth_token = '2c23e64b67af9d2db8526c58eece163a'
client = Client(account_sid, auth_token)

# Twilio Sandbox WhatsApp number
from_whatsapp = 'whatsapp:+14155238886'  # Example Twilio number
to_whatsapp = 'whatsapp:+1234567890'    # My WhatsApp number

patient_data = {}

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route("/webhook", methods=["POST"])
def webhook():
    print('hello')
    message = request.form.get('Body')
    from_number = request.form.get('From')

    resp = MessagingResponse()

    if not patient_data.get('name'):
        patient_data['name'] = message
        resp.message('Got it. What is your date of birth?')
    elif not patient_data.get('dob'):
        patient_data['dob'] = message
        resp.message('What is your gender?')
    elif not patient_data.get('gender'):
        patient_data['gender'] = message
        resp.message('What is your address?')
    else:
        patient_data['address'] = message
        resp.message('Thank you! Your information has been saved.')

    return str(resp)

@app.route("/send_message", methods=["GET"])
def send_message():
    try:
        message = client.messages.create(
            body="Hello, this is your WhatsApp bot!",
            from_=from_whatsapp,
            to=to_whatsapp
        )
        return jsonify({"message": "Message sent", "sid": message.sid})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
